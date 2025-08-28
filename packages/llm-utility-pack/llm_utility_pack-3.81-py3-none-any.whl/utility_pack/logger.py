import datetime, pytz, inspect, traceback, logging

def get_datetime_brasilia(return_string: bool = True):
    now = datetime.datetime.now(pytz.timezone('America/Sao_Paulo'))
    return now.strftime("%d/%m/%Y - %H:%M:%S") if return_string else now

def log_exception():
    frame = inspect.currentframe().f_back

    func_name = frame.f_code.co_name
    filename = frame.f_code.co_filename
    line_no = frame.f_lineno

    arg_info = inspect.getargvalues(frame)
    params = str({arg: arg_info.locals.get(arg) for arg in arg_info.args})

    detailed_exp = traceback.format_exc()
    msg = f"{get_datetime_brasilia()} ~ Error (Log call: [{filename}.{func_name}():{line_no}]).\nStack: {detailed_exp}\nParams: {params[:100]}"
    
    logging.error(msg)
