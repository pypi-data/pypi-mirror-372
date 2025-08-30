import logging,os
from scilens.config.models import ReportConfig
from scilens.utils.template import template_render_infolder
from scilens.report.assets import get_image_base64,get_image_base64_local,get_logo_image_src
class HtmlReport:
	def __init__(A,config,alt_config_dirs,working_dir=None):A.config=config;A.alt_config_dirs=alt_config_dirs;A.working_dir=working_dir
	def process(A,data):
		G='meta';logging.info(f"Processing html report")
		if A.config.logo and A.config.logo_file:raise ValueError('logo and logo_file are exclusive.')
		H=A.config.logo;B=None
		if A.config.logo_file:
			C=A.config.logo_file
			if os.path.isabs(C):
				B=C
				if not os.path.isfile(D):raise FileNotFoundError(f"Logo file '{A.config.logo_file}' not found.")
			else:
				E=list(set([A.working_dir]+A.alt_config_dirs))
				for I in E:
					D=os.path.join(I,C)
					if os.path.isfile(D):B=D;break
				if not B:raise FileNotFoundError(f"Logo file '{A.config.logo_file}' not found in {E}.")
		F=None
		if A.config.debug:F=A.config.model_dump_json(indent=4)
		return template_render_infolder('index.html',{'image':H or get_logo_image_src(B),'execution_dir':A.working_dir,'config_html':A.config.html,'config_html_json':A.config.html.model_dump_json(),G:data.get(G),'data':{'files':data.get('processor_results')},'debug':F},template_dir=os.path.join(os.path.dirname(os.path.realpath(__file__)),'templates'))