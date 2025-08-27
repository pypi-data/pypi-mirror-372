from ibm_wos_utils.feedback.batch.utils.date_util import DateUtil

class TimeWindowUtils():

    def __init__(self, logger):
        self.logger = logger
    
    def get_time_windows(self, is_history_run: bool, parameters: dict, last_updated_timestamp: str) -> list:
        '''
        Calculates the time windows for the given start date and end date. If the start and end dates 
        are not specified then it is assumed that the job is computing metrics for regular batch flow and it 
        considers the start_time as last_processed_time and end_time = None
        
        Case 1: Regular flow(history_runs = false), last_updated_timestamp = "xxx". 
                Returns the single time window with start_time = last_updated_timestamp, end_time = None
        Case 2: history_runs = true , start_date = "xxx" , end_date = "yyy"
                Returns the single time window with given start date and enddate.
        Case 3: history_runs = true , start_date = "xxx" , end_date = "yyy", compute_windows = N evaluations
                Divides the specified time window by the number of evaluations specified in the compute_windows option and 
                returns the multiple time windows with different start and end times
        Case 4: history_runs = true , start_date = "xxx" , end_date = "yyy", evalute_using_schedule = True
                Divides the specified time window based on the given repeat type and repeat interval and 
                returns the multiple time windows with different start and end times
               
        '''
        
        time_windows = list()
        end_time = None

        if not is_history_run:
            #For the regular flow, consider start_time = last_updated_time  and end_time = none
            start_time = last_updated_timestamp
            time_windows.append([start_time, end_time])
            return time_windows
        else:
            #start_time and end_time values are given for the historical runs usecase only. 
            history_runs_payload = parameters.get("history_runs_payload")
            start_time = history_runs_payload.get("start_date")
            end_time = history_runs_payload.get("end_date")
            compute_windows = history_runs_payload.get("compute_windows")
            evaluate_using_schedule = history_runs_payload.get("evaluate_using_schedule")
            
            if evaluate_using_schedule is not None and evaluate_using_schedule is True:
                repeat_type = history_runs_payload.get("repeat_type")
                repeat_interval = history_runs_payload.get("repeat_interval")
                time_windows = self.get_time_windows_for_evaluate_schedule_option(start_time, end_time, repeat_type, repeat_interval)
            elif compute_windows is not None and int(compute_windows) > 0:
                compute_windows = int(compute_windows)
                time_windows = self.get_time_windows_for_compute_windows_option(start_time, end_time, compute_windows)
            else:
                compute_windows = 1
                time_windows = self.get_time_windows_for_compute_windows_option(start_time, end_time, compute_windows)
            
        return time_windows

    def get_time_windows_for_compute_windows_option(self, start_time: str, end_time: str, compute_windows: int) -> list: 
        '''
        Calculates the multiple time windows for the given start date and end date 
        by dividing the specified time window with the number of evaluations given in compute_windows
        '''
        time_windows = list()

        if compute_windows == 1:
            time_windows.append([start_time, end_time])
            return time_windows
        
        time_diff_in_seconds = DateUtil.get_time_diff_in_seconds(
            from_time=start_time,to_time=end_time)
        seconds_per_window = time_diff_in_seconds/compute_windows

        self.logger.info("Calculating time windows for the start_date {} and end_date {} using the compute_windows option".format(start_time,end_time))
        
        window_start_time = start_time
        for x in range(0, compute_windows):
            window_end_time = DateUtil.get_datetime_with_time_delta(time=window_start_time,
                                unit="second",count=seconds_per_window,previous=False)
                            
            time_windows.append([window_start_time, window_end_time])
            #assign the window_end_time to window_start_time for the next time window
            window_start_time = window_end_time
        
        self.logger.info("Finished calculating time windows {} using the compute_windows option".format(time_windows))
        
        return time_windows

    def get_time_windows_for_evaluate_schedule_option(self, start_time: str, end_time: str, repeat_type: str, repeat_interval: int) -> list: 
        '''
        Calculates the multiple time windows for the given start date and end date 
        by dividing the specified time window with the schedule frequency 
        given in the repeat_type and repeat_interval
        '''
        time_windows = list()
        window_start_time = start_time
        window_end_time = None

        self.logger.info("Calculating time windows for the start_date {} and end_date {} using evaluate_using_schedule option".format(start_time,end_time))
        while DateUtil.get_datetime_str_as_time(window_start_time) < DateUtil.get_datetime_str_as_time(end_time):

            repeat_type, repeat_interval = self.__get_modified_repeat_type_interval(repeat_type, repeat_interval)
            window_end_time = DateUtil.get_datetime_with_time_delta(time=window_start_time,
                                unit=repeat_type, count=repeat_interval, previous=False)
    
            if DateUtil.get_datetime_str_as_time(window_end_time) > DateUtil.get_datetime_str_as_time(end_time):
                window_end_time = end_time
            time_windows.append([window_start_time, window_end_time])
            #assign the window_end_time to window_start_time for the next time window
            window_start_time = window_end_time

        self.logger.info("Finished calculating time windows {} using the evaluate_using_schedule option".format(time_windows))

        return time_windows

    def __get_modified_repeat_type_interval(self, repeat_type: str, repeat_interval: int):

        if repeat_type == "week":
            #convert weeks into the days
            repeat_interval = repeat_interval * 7
            repeat_type = "day"
        elif repeat_type in ["month","year"]:
           raise Exception("repeat_type {} is not supported".format(repeat_type))
        
        return repeat_type, repeat_interval


    