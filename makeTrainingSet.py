import csv
from features import *
import glob
from pprint import *

from htmlDiff import *
import pdb

# Return a list of all files from a base directory.
def getSubDirs(baseDir):
    return sorted(glob.glob(baseDir))

if __name__ == '__main__':
    # Open CSV for writing training set into.
    csvFile = open('training_vectors.csv', 'wb')
    csvWriter = csv.writer(csvFile, delimiter=',')
    fieldNames = ['fullText', 'otherInfo', 'rawTextChange', 'rawAttributeChange', 'afterText', 'elementType', 'afterAttribute', 'op']

    # Write header row for CSV readability.
    headerRow = getCSVHeaders()
    headerRow.append('class')
    csvWriter.writerow(headerRow)

    # Create training set from all malicious data set:
    # Get list of files.
    malDirs = getSubDirs('ground_truth/malware_traffic_analysis/*')
    # Remove broken test cases.
    malDirs.remove('ground_truth/malware_traffic_analysis/2015_07_13')
    malDirs.remove('ground_truth/malware_traffic_analysis/2015_08_14-2')
    malDirs.remove('ground_truth/malware_traffic_analysis/2015_09_02')
    malDirs.remove('ground_truth/malware_traffic_analysis/2015_10_18')
    malDirs.remove('ground_truth/malware_traffic_analysis/2015_10_18-2')

    for malDir in malDirs:
        # Get feature vectors for each pair of files.
        print malDir
        file1 = malDir + '/before.html'
        file2 = malDir + '/after.html'
        diff = htmldiff(file1, file2)
        try: 
            diff['afterText'].rstrip()
        except:
            pass
        try: 
            diff['rawChange'].rstrip()
        except:
            pass
        features = getFeatures(diff)
        # For each feature, write class '1' for malicious.
        for key, feature in enumerate(features):
            feature.append('malicious')
            # Write feature vector to training set csv.
            csvWriter.writerow(feature)

    # Get list of files.
    file1 = 'ground_truth/benign/2015_10_28_10/cnn.com.html'
    file2 = 'ground_truth/benign/2015_10_29_10/cnn.com.html'
    # Get feature vectors for each file.
    print file1
    diff = htmldiff(file1, file2)
    try: 
        diff['afterText'].rstrip()
    except:
        pass
    try: 
        diff['rawTextChange'].rstrip()
    except:
        pass
    features = getFeatures(diff)
    # For each feature, write class '0' for benign.
    for key, feature in enumerate(features):
        feature.append('benign')
        # Write feature vector to training set csv.
        csvWriter.writerow(feature)

    csvFile.close()
