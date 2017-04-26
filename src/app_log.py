import time

'''
Write to log file if set; otherwise standard print
'''
def app_log(log_file, statement, initialize = False):
    write_mode = "a"
    if initialize:
        write_mode = "w"
    if log_file:
        with open(log_file, write_mode) as log_file:
            timestamp = time.strftime("%b %d %Y %H:%M:%S")
            log_file.write("{} - {}\n".format(timestamp, statement))
            log_file.close()
    else:
        print(statement)
