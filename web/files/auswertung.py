import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd


def secondDeriv(x1, x2, x3):
    """
        calculates the second derivation from given points
    :param x1: first point
    :param x2: second point
    :param x3: third point
    """
    diff_x2_x3 = x3 - x2
    diff_x1_x2 = x2 - x1
    return diff_x2_x3 - diff_x1_x2


def nextPoint(x1, x2, x3):
    """
        predicts next point from given points
    :param x1: first point
    :param x2: second point
    :param x3: third point
    """
    return x3 + (x3 - x2) + secondDeriv(x1, x2, x3)

def nextPoints(vec, stepSize):
    """
        creates new vector with predicted values
    :param vec: list with datapoints
    :param stepSize: stepSize for new values that will be predicted
    """
    maxsize = len(vec)
    newVec = list()
    for pos in range(0, maxsize - stepSize * 3, stepSize):
        first = vec[pos]
        second = vec[pos + stepSize]
        third = vec[pos + stepSize * 2]
        newVec.append(nextPoint(first, second, third))
    return newVec
        
def testNextPoints(xy_vector):
    """
        prints new predicted points from a vector list with x,y coordinates
    :param xy_vector: list of 2d vector, first index is the element, second is the x-value
    """
    vec_len = len(xy_vector) - 2
    for i in range(vec_len):
        print(nextPoint(xy_vector[i][1], xy_vector[i + 1][1], xy_vector[i + 2][1]))


def meanPoints(vec, step):
    """
        creates new list with a mean step between points that is defined in step parameter
    :param vec: list of floating points
    :param step: stepsize between points in vec
    """
    newVec = list()
    stop = len(vec) - (len(vec) % step)
    for i in range(0, stop, step):
        vecSum = 0
        for j in range(step):
            vecSum += vec[i+j]
        newVec.append(vecSum/step)
    return newVec


def plotdata(filepath, pos, step):
    """
        creates a plot with original and predicted data
    :param filepath: filepath of csv file
    :param pos: index of P10 - or P2 - clumn in CSV file
    :param step: number of Points that are displayed as one
    """
    sns.set_style("darkgrid", {'axes.axisbelow': False})
    csvdata = pd.read_csv(filepath)
    testvalues = csvdata[csvdata.columns[pos]]
    lnext = list()
    lnext.append(0)
    lnext.append(0)
    lnext.append(0)
    # calculate next points
    lnext.extend(nextPoints(vec = testvalues, stepSize=1))
    # calculate mean every "step" - points
    newdata = pd.DataFrame(data = meanPoints(vec = testvalues, step=step))
    newdata[1] = meanPoints(vec = testvalues, step=step)
    newdata[2] = meanPoints(vec = lnext, step=step)

    plt.figure(figsize=(8, 6), dpi=100)    
    plt.plot(newdata[1], label="original")
    plt.plot(newdata[2], label="predicted")
    plt.xlabel("Zeit")
    plt.ylabel("P_10")
    plt.title("Zeit vs. P_10 Wert")
    plt.legend()
    plt.show()
    print("Anzahl der Messpunkte: ", len(newdata[1]))
    print("Mittlere P-Wertdifferenz: ", sum(abs(newdata[1] - newdata[2]))/len(newdata[1]))
    print()

plotdata(filepath="data\\luftdaten\\2016-10-29\\archive.luftdaten.info_2016-10-29_2016-10-29_sds011_sensor_219.csv",
         pos=7, step=20)

def boxplot(filepath, pos):
    sns.set(style="ticks", palette="pastel")
    csvdata = pd.read_csv(filepath)
    sns.boxplot(data=csvdata[csvdata.columns[pos]])
    sns.despine(offset=10, trim=True)
    plt.show()

boxplot(filepath="data\\luftdaten\\2016-10-29\\archive.luftdaten.info_2016-10-29_2016-10-29_sds011_sensor_219.csv",
        pos=7)
