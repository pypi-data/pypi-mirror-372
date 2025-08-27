# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2020, 2021
# The source code for this program is not published or other-wise divested of its trade 
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

import sys
import numpy as np
import math, copy
try:
    from pyspark.sql import DataFrame
    from pyspark.mllib.evaluation import MulticlassMetrics, RegressionMetrics, BinaryClassificationMetrics
    from pyspark.sql.functions import col, expr, lit
    from pyspark.ml.feature import StringIndexer
    from pyspark.ml import Pipeline
except ImportError as ie:
    pass
from ibm_wos_utils.feedback.batch.utils import constants

class MetricsUtils():
    
    def __init__(self, logger, spark_version):
        self.logger = logger
        self.is_spark_version_greater_than_3 = self.is_spark_library_version_greater_than_3(spark_version)
      
    '''
    Find the true label value from the probability. For binary model, true label is always 
    at index position 1 in the probability array.
    '''
    def detect_true_label(self, data, probability_col, prediction_col, sorted_labels):

        # get the first row from the dataset to identify true label which is
        # at index position 1 in the probability array
        result = data.select(probability_col, prediction_col).first()
        probability_val = result[probability_col]
        prediction_val = result[prediction_col]

        self.logger.info("Detecting the true label from the probability array {} and the predicted value is {}".format(
            probability_val, prediction_val))

        prob_arr = np.array(probability_val)
        # get the max value of index location
        win_prob_index_position = np.argmax(prob_arr)
        self.logger.info("Winning Probability Index Position {}".format(
            win_prob_index_position))

        true_label = None
        if win_prob_index_position == 1:
            # If the winning probability is at index 1 then predicted value is the true label
            true_label = prediction_val
            self.logger.info("Winning Probability Index Position: {} and True label: {}".format(
                win_prob_index_position, true_label))
        else:
            # There are only 2 values in the probability array for binary classfication models.
            # If the winning probaility is 0, then find the value from the label's list which is not
            # equal to the predicted value
            for val in sorted_labels:
                if val != prediction_val:
                    true_label = val
                    self.logger.info("Winning Probability Index:  is at {} and True label: {}".format(
                        win_prob_index_position, true_label))

        return true_label


    def get_string_indexer_order_type(self, sorted_labels, true_label):

        label_index = 0
        # default ordering is aplhabetic ascending order
        string_order_type = "alphabetAsc"
        for val in sorted_labels:
            if val == true_label and label_index == 1:
                string_order_type = "alphabetAsc"
                self.logger.info("True label {} and label_index {} assigning string order type {}".
                            format(true_label, label_index, string_order_type))
            elif val == true_label and label_index == 0:
                string_order_type = "alphabetDesc"
                self.logger.info("True label {} and label_index {} assigning string order type {}".
                            format(true_label, label_index, string_order_type))
            label_index = label_index + 1

        return string_order_type
    
    def get_label_query_expr(self, label_indexes, col_name):
        
        label_query = "case "
        for label_val_name, index in label_indexes.items():
            label_str = "when `{0}` = '{1}' then {2} ".format(
                col_name, label_val_name, float(index))
            label_query += label_str
        label_query += "else -1 end"
        
        return label_query
    
    def find_missing_labels_index(self, unique_labels, label_index_dict, probab_index_len):
        ''' Assigns the index for the missing label index values
        from the unused indexes in the probability array
        For eg: Here is the sample feedback data
            label    prediction  probability
            class A  class A     [1.0, 0.0, 0.0, 0.0]
            class C  class B     [0.0, 1.0, 0.0, 0.0]
            class B  class B     [0.0, 1.0, 0.0, 0.0]
            class D  class D     [0.0, 0.0, 0.0, 1.0]
            Indexes assigned Class A - 0.0, Class B - 1.0, Class D - 3.0 , Class C - ?
        '''

        missing_label_index_vals = dict()
        label_index_keys = list(label_index_dict)

        label_index_vals = list(label_index_dict.values())
        available_indexes = []
        for label_index in range(0, probab_index_len):
            if label_index not in label_index_vals:
                available_indexes.append(label_index)
        
        self.logger.info("Unique labels {}".format(unique_labels))

        idx = 0
        for label in unique_labels:
            if label not in label_index_keys:
                self.logger.info("label {} is missing. Assigned index is {}".format(label, available_indexes[idx]))
                missing_label_index_vals[label] = available_indexes[idx]
                idx = idx + 1
        self.logger.info("Missing label indexes: {}".format(missing_label_index_vals))
        return missing_label_index_vals
    
    def find_labels_index_from_predictions(self, predicted_data, label_indexes_dict):
        '''
        Finds the label index values from the data where label != prediction
        '''
        label_index_vals = list(label_indexes_dict.values())
        self.logger.info("Found label index values from label wining probability index position {}".format(label_indexes_dict))
        for row in predicted_data:
            label, prediction, probability = row
            # get the max value of index location
            win_prob_index_position = np.argmax(np.array(probability))

            if label != prediction and prediction not in label_indexes_dict and \
                    win_prob_index_position not in label_index_vals:
                label_indexes_dict[prediction] = win_prob_index_position
                self.logger.info("Assigning index {} for label {} from prediction wining probability index position".format(win_prob_index_position, prediction))
                
        return label_indexes_dict
                        
    def mainpulate_data(self, data, model_type, label_col, prediction_col, probability_col):
        
        pred_probab_df = None
        pred_df = None
        
        try:
            label_col_type = dict(data.dtypes)[label_col]
        except KeyError as ex:
            #Fallback to the lowercase, if the label column is not found with original case
            label_col = label_col.lower()
            prediction_col = prediction_col.lower()
            
        label_col_type = dict(data.dtypes)[label_col]
        prediction_col_type = dict(data.dtypes)[prediction_col]

        distinct_labels = []
        if model_type != constants.REGRESSION_MODEL_TYPE:
            label_indexes = dict()
            if label_col_type in constants.CLASSIFICATION_CAST_DATA_TYPES:
                data = data.withColumn(label_col, col(label_col).cast('string'))

            if model_type == constants.BINARY_CLASSIFICATION_MODEL_TYPE:
                # Find the distinct labels from the label column
                distinct_labels = [x[label_col]
                                for x in data.select(label_col).distinct().collect()]
                sorted_labels = sorted(distinct_labels)
                true_label = self.detect_true_label(
                    data, probability_col, prediction_col, sorted_labels)
                string_order_type = self.get_string_indexer_order_type(
                    sorted_labels, true_label)
                
                string_indexer = StringIndexer(
                    inputCol=label_col, outputCol=label_col + "_index", stringOrderType=string_order_type)
                
                string_indexer_model = string_indexer.fit(data)
                distinct_labels = string_indexer_model.labels
                self.logger.info("Distinct Labels:{}".format(distinct_labels))
                df = string_indexer_model.transform(data)
                
                label_col = label_col + "_index"

                label_encode_index = 0.0
                for label in distinct_labels:
                    label_indexes[label] = label_encode_index
                    label_encode_index += 1
                
                prediction_query_str = self.get_label_query_expr(label_indexes, prediction_col)
                
            if model_type == constants.MULTI_CLASSIFICATION_MODEL_TYPE:
                
                # Fetches the distinct label, prediction and  probability values to find the index for 
                # the labels from probability column and replace the labels in ground truth and 
                # prediction values with index values
                unique_scored_data = data.dropDuplicates([label_col, prediction_col]) #fetches the distinct label and prediction columns data
                unique_scored_data = unique_scored_data.select(label_col, prediction_col, probability_col).collect()
    
                predictions_data = list()
                idx = 0
                probabilites_index_len = 0
                unique_labels = []
                unique_scored_data_len = len(unique_scored_data)
                
                for row in unique_scored_data:
                    label, prediction, probability = row
                    label_str = str(label)
                    prediction_str = str(prediction)

                    probabilites_index_len = len(probability)
                    idx = idx + 1
                    prob_arr = np.array(probability)
                    # get the max value of index location
                    win_prob_index_position = np.argmax(prob_arr)
                    if label_str == prediction_str:
                        label_indexes[label_str] = win_prob_index_position
                    elif label_str != prediction_str and prediction_str not in label_indexes:
                        row = label_str, prediction_str, probability
                        predictions_data.append(row)

                    if label_str not in unique_labels:
                        unique_labels.append(label_str)

                    ## Check whether all the labels have indexes assigned, if not then find the missing index for the labels 
                    # and assign the index from the probability array
                    if unique_scored_data_len == idx and len(label_indexes) != probabilites_index_len:
                        label_indexes = self.find_labels_index_from_predictions(predictions_data, label_indexes)
                        if len(label_indexes) != probabilites_index_len:
                            self.logger.info("Finding the missing indexes for the ground truth label values")
                            missing_label_index_vals = self.find_missing_labels_index(unique_labels, label_indexes, probabilites_index_len)
                            label_indexes.update(missing_label_index_vals)
                        
                label_indexes = dict(sorted(label_indexes.items(), key=lambda x: x[1]))
                self.logger.info("Label index mapping:{}".format(label_indexes))
                distinct_labels = list(label_indexes)
                label_query_str = self.get_label_query_expr(label_indexes, label_col)
                prediction_query_str = self.get_label_query_expr(label_indexes, prediction_col)
                
                df = data.withColumn(label_col, expr(label_query_str))
                df = df.withColumn(label_col, col(label_col).cast('double'))
            
            df = df.withColumn(prediction_col, expr(prediction_query_str))
            df = df.withColumn(prediction_col, col(prediction_col).cast('double'))
            df = df.withColumn(probability_col, col(probability_col).cast('array<double>'))
            if self.is_spark_version_greater_than_3:
                # Spark 3.x Binary and MultiClassification API's expects weight value to be present along with probability values
                # Assign the default weight value to 1
                df = df.withColumn("weight", lit(1.0).cast('double'))
                pred_probab_df = df.select(prediction_col, label_col, "weight", probability_col)
            if (model_type == constants.BINARY_CLASSIFICATION_MODEL_TYPE) or \
                (model_type == constants.MULTI_CLASSIFICATION_MODEL_TYPE and (not self.is_spark_version_greater_than_3)):
                pred_df = df.select(prediction_col, label_col)

        if model_type == constants.REGRESSION_MODEL_TYPE:

            # cast the int/long/float values to double as the spark ml accepts the
            # label and prediction values to be in doouble data type
            # cast the double type column values to double as the column will have both int and double values
            if label_col_type in constants.REGRESSION_MODEL_DATA_TYPES:
                data = data.withColumn(label_col, col(label_col).cast('double'))
            if prediction_col_type in constants.REGRESSION_MODEL_DATA_TYPES:
                data = data.withColumn(prediction_col, col(prediction_col).cast('double'))
                
            pred_df = data.select(prediction_col, label_col)

        return pred_df, pred_probab_df, distinct_labels

    '''
    Generate the quality metrics  based on the model type using the spark ml library.
    For binary models, it detects the true label from the probability values and 
    true label will always be at index position 1 and same will be considered in the 
    order of labels while generating the confusion matrix. For multiclass, it finds the label 
    index position  from the probability array and the same order of labels will be considered 
    while generating the confusion matrix.
    '''

    def compute_quality_metrics(self, sc, data, model_type, label_col, prediction_col, probability_col, counts):

        self.logger.info("Computing the quality metrics for model type: {}".format(model_type))
        pred_labels_df, pred_labels_prob_df, distinct_labels = self.mainpulate_data(data, model_type, label_col, prediction_col, probability_col)
        pred_labels = None
        pred_labels_prob = None
        self.logger.info("Fetching the rdd from the predictions and probabilites dataframe")
        if model_type == constants.BINARY_CLASSIFICATION_MODEL_TYPE and self.is_spark_version_greater_than_3:
            #predictionAndLabels = df1.rdd.map(tuple)
            pred_labels = pred_labels_df.rdd
            pred_labels_prob = pred_labels_prob_df.rdd
        elif model_type == constants.MULTI_CLASSIFICATION_MODEL_TYPE and self.is_spark_version_greater_than_3:
            pred_labels_prob = pred_labels_prob_df.rdd
        else:
            pred_labels = pred_labels_df.rdd

        metrics = dict()
        quality_metric, confusion_matrix = self.get_metrics(
            model_type, pred_labels, pred_labels_prob, distinct_labels)

        metrics["quality_metric"] = quality_metric
        metrics["total_records"] = counts['records_count']
        if 'borrowed_records' in counts:
            metrics["borrowed_records"] = counts["borrowed_records"]
        if model_type != constants.REGRESSION_MODEL_TYPE:
            self.logger.info("Labels {}".format(distinct_labels))
            self.logger.info("confusion_matrix {}".format(confusion_matrix))
            metrics["confusion_matrix"] = confusion_matrix.tolist()
            metrics["labels"] = distinct_labels

        self.logger.info("Quality metrics {} for model type:{}".format(
            quality_metric, model_type))

        return metrics
        
    
    def get_metrics(self, model_type, prediction_labels = None, prediction_labels_probabilities = None, distinct_labels = None):

        quality_metric = dict()
        confusion_matrix = list()
        # use the set_printoptions to ignore the scientific notation of digits in the confusion matrix
        np.set_printoptions(suppress=True)

        if model_type == constants.MULTI_CLASSIFICATION_MODEL_TYPE:

            if self.is_spark_version_greater_than_3:
                metrics_mc = MulticlassMetrics(prediction_labels_probabilities)
                #log_loss metrics is supported from spark 3.x version
                log_loss   = metrics_mc.logLoss()
            else:
                metrics_mc = MulticlassMetrics(prediction_labels)

            weighted_recall = metrics_mc.weightedRecall
            weighted_precision = metrics_mc.weightedPrecision
            weighted_f_measure = metrics_mc.weightedFMeasure(1.0)
            accuracy = metrics_mc.accuracy
            weighted_false_positive_rate = metrics_mc.weightedFalsePositiveRate
            weighted_true_positive_rate = metrics_mc.weightedTruePositiveRate

            # confusion matrix fetches the labels in ascending order
            confusion_matrix = metrics_mc.confusionMatrix().toArray()
            
            quality_metric["accuracy"] = accuracy
            quality_metric["weighted_true_positive_rate"] = weighted_true_positive_rate
            quality_metric["weighted_recall"] = weighted_recall
            quality_metric["weighted_precision"] = weighted_precision
            quality_metric["weighted_f_measure"] = weighted_f_measure
            quality_metric["weighted_false_positive_rate"] = weighted_false_positive_rate
            if self.is_spark_version_greater_than_3:
                quality_metric["log_loss"] = log_loss

        elif model_type == constants.BINARY_CLASSIFICATION_MODEL_TYPE:

            binary_metrics = BinaryClassificationMetrics(prediction_labels)
            if self.is_spark_version_greater_than_3:
                mc_metrics = MulticlassMetrics(prediction_labels_probabilities)
                log_loss   = mc_metrics.logLoss()
            else:
                mc_metrics = MulticlassMetrics(prediction_labels)

            accuracy = mc_metrics.accuracy
            area_under_roc = binary_metrics.areaUnderROC
            area_under_pr = binary_metrics.areaUnderPR
            
            # Find's the True positive rate for the true label 1.0.
            # True label is always at index position 1 in the array [0.0, 1.0]
            true_label_index = 1.0
            if len(distinct_labels) == 1:
                # If there is only one label in the dataset then consider label at index position 0
                true_label_index = 0.0
                
            true_positive_rate = mc_metrics.truePositiveRate(true_label_index)
            # Find's the False positive rate for the true label 1.0.
            false_positive_rate = mc_metrics.falsePositiveRate(true_label_index)
            # Find's the Recall for the true label 1.0.
            recall = mc_metrics.recall(true_label_index)
            # Find's the Precision for the true label 1.0.
            precision = mc_metrics.precision(true_label_index)
            # Find's the f1_measure for the true label 1.0.
            f1_measure = mc_metrics.fMeasure(true_label_index)
			
            confusion_matrix = mc_metrics.confusionMatrix().toArray()

            quality_metric["accuracy"] = accuracy
            quality_metric["true_positive_rate"] = true_positive_rate

            quality_metric["recall"] = recall
            quality_metric["precision"] = precision
            quality_metric["false_positive_rate"] = false_positive_rate
            quality_metric["area_under_roc"] = area_under_roc
            quality_metric["area_under_pr"] = area_under_pr
            quality_metric["f1_measure"] = f1_measure
            if self.is_spark_version_greater_than_3:
                quality_metric["log_loss"] = log_loss

        elif model_type == constants.REGRESSION_MODEL_TYPE:
            metrics = RegressionMetrics(prediction_labels)

            explained_variance = metrics.explainedVariance
            mean_absolute_error = metrics.meanAbsoluteError
            mean_squared_error = metrics.meanSquaredError
            r2 = metrics.r2
            root_mean_squared_error = metrics.rootMeanSquaredError

            quality_metric["explained_variance"] = explained_variance
            quality_metric["mean_absolute_error"] = mean_absolute_error
            quality_metric["mean_squared_error"] = mean_squared_error
            quality_metric["r2"] = r2
            quality_metric["root_mean_squared_error"] = root_mean_squared_error

        quality_metric = self.remove_nan_values(quality_metric)
        return quality_metric, confusion_matrix
    
    def is_spark_library_version_greater_than_3(self, spark_version):
        #Get the first digit from the spark version 3.x.x
        version = int(str(spark_version).split('.')[0])
        if version >= 3:
            return True
        else:
            return False
        
    def remove_nan_values(self, quality_metrics: dict) -> dict:
        metrics = copy.deepcopy(quality_metrics)
        for key, value in quality_metrics.items(): 
            if math.isnan(value):
                self.logger.info("Removing Nan value for {} from the metrics".format(key))
                metrics.pop(key)
                
        return metrics




