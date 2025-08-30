import datetime as dt
from scilens.app import pkg_name,pkg_version,pkg_homepage,product_name,powered_by
class ReportAppInfo:
	def info(C):A='name';B=dt.datetime.now(dt.timezone.utc).strftime('%Y');return{A:product_name,'version':pkg_version,'homepage':pkg_homepage,'copyright':f"© {B} {powered_by[A]}. All rights reserved",'powered_by':powered_by}