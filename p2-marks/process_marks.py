import numpy as np
import pandas as pd

def main():
	df = pd.read_csv("Student_marks_list.csv")

	numeric = df.columns[1:]
	df[numeric] = df[numeric].apply(pd.to_numeric)
	sub_topper = df[numeric].idxmax(axis=0)
	for sub, i in sub_topper.iteritems():
		print("Topper in %s is %s" % (sub, df.iloc[i]["Name"]))
	print()	

	avg = df.mean(axis=1)
	rank = np.argpartition(avg,-3)[-1:-4:-1]
	print("best students in class are ", end="")
	for _,i in rank.iteritems():
		print(" %s " %  df.iloc[i]["Name"], end="")
	print("\n\nBig-O: O^2\n")

if __name__ == '__main__':
	main()


"""

"""