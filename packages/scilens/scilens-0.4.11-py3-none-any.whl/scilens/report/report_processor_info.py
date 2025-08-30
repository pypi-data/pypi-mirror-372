class ReportProcessorInfo:
	def info(G,processor,data):
		E='comparison';B=processor;A={'name':B};F=B in['Compare','ExecuteAndCompare'];A['has_multiple_datasets']=len(data)>1
		if F:
			A['is_compare']=True;C=0
			for D in data:
				if D.get(E)and D[E].get('metrics'):C+=1
			A['datasets_metrics']=C
		return A