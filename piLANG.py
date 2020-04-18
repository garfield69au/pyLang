"""
piLANG.py

Overview
--------
piLANG is a data quality validation tool that implements
the LANG data quality algorithms 
(see: Zhang, R., Indulska, M., & Sadiq, S. (2019). Discovering Data Quality Problems: The Case of Repurposed Data. Business and Information Systems Engineering, 61(5), 575–593. https://doi.org/10.1007/s12599-019-00608-0


USAGE
--------

$ python piLANG -i <source_file_name> -m <meta_data_file_name> -o <outputfile_prefix> --profile --validate 

OUTPUT:
--------
The outout from piLANG depends on what you want to achieve.
the --profile switch will trigger a data profile the source data 
and output the results as an Excel spreadsheet.

The --validate switch will trigger a validation of the source
data and the output will be a Spreadsheet of data quality
validation errors.



Change History:
-----------------
Version: 1.0    18/04/2020  Shane J. Downey
- Initial release


"""
#!/usr/bin/python

import sys, getopt


class piLANG:

    @staticmethod
    def cleanLine(line:str):
        """
        The standard python output of a list includes characters [.]. and '. 
        This routine strips those characters off the output.
        """
        result = line
        
        for c in ["[","]","'"]:
            result=result.replace(c,"")
        return result

        
    @staticmethod
    def validate(inputFilename:str, outputFilename:str):
        pass

    @staticmethod
    def profile(inputFilename:str, outputFilename:str):
        pass
        
        
def main(argv):
    inputfile = ""
    outputfile = ""
    metafile=""
    
    try:
        opts, args = getopt.getopt(argv,"hi:o:m:",["ifile=","ofile=","metafile="])
    except getopt.GetoptError:
        print ("piLANG.py -i <inputfile> -o <outputfile>")
        sys.exit(2)

    if (len(opts)!=2):
        print("Missing args.")
        print("piLANG.py -i <inputfile> -o <outputfile>")
        sys.exit(2)

 
    for opt, arg in opts:
        if opt == "-h":
            print ("piLANG.py -i <inputfile> -o <outputfile>")
            sys.exit()
        elif opt in ("-i", "--ifile"):
            inputfile = arg.strip()
        elif opt in ("-o", "--ofile"):
            outputfile = arg.strip()
   
    piLANG.parse(inputfile, outputfile)
    sys.exit()


if  __name__ =='__main__':
    main(sys.argv[1:])
