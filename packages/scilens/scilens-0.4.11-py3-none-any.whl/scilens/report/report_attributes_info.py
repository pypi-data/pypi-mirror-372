from scilens.config.models import ReportConfig
from scilens.utils.time_tracker import TimeTracker
class ReportAttributesInfo:
	def info(E,config,task_name):A=config;C=A.title if A.title else A.title_prefix+' '+task_name;D=TimeTracker();B=D.get_data()['start'];return{'title':C,'description':A.description,'execution_utc_date':B['date'],'execution_utc_time':B['time']}