# Your Agent for solving Raven's Progressive Matrices. You MUST modify this file.
#
# You may also create and submit new files in addition to modifying this file.
#
# Make sure your file retains methods with the signatures:
# def __init__(self)
# def Solve(self,problem)
#
# These methods will be necessary for the project's main method to run.

# Install Pillow and uncomment this line to access image processing.
from PIL import Image
from PIL import ImageChops
import math
import numpy
import itertools

class Agent:
    # The default constructor for your Agent. Make sure to execute any
    # processing necessary before your Agent starts solving problems here.
    #
    # Do not add any variables to this signature; they will not be used by
    # main().
    def __init__(self):
        pass

    # The primary method for solving incoming Raven's Progressive Matrices.
    # For each problem, your Agent's Solve() method will be called. At the
    # conclusion of Solve(), your Agent should return an int representing its
    # answer to the question: 1, 2, 3, 4, 5, or 6. Strings of these ints
    # are also the Names of the individual RavensFigures, obtained through
    # RavensFigure.getName(). Return a negative number to skip a problem.
    #
    # Make sure to return your answer *as an integer* at the end of Solve().
    # Returning your answer as a string may cause your program to crash.
    def Solve(self,problem):
        answer = -1
        probType = problem.problemType
        if probType == '2x2':
            return answer
        if probType == '3x3' and problem.name=='Basic Problem D-01':
            answer = solve3x3(problem)
        return answer


def solve3x3(problem):
    # Get images for the given problem
    images = getImages(problem)

    # Process the image and return values related to each individual image
    pixelRatios = getPixelRatios(images)

    # place figures and potential answers into two separate dictionaries
    figures = {}
    answers = {}
    for img in images:
        if img == '1':
            answers.update({'1': images['1']})
        elif img == '2':
            answers.update({'2': images['2']})
        elif img == '3':
            answers.update({'3': images['3']})
        elif img == '4':
            answers.update({'4': images['4']})
        elif img == '5':
            answers.update({'5': images['5']})
        elif img == '6':
            answers.update({'6': images['6']})
        elif img == '7':
            answers.update({'7': images['7']})
        elif img == '8':
            answers.update({'8': images['8']})
        else:
            figures.update({img: images[img]})

    # Begin constructing answer
    agentAnswer = generateAnswer(figures, answers, pixelRatios)

    if agentAnswer == None:
        return -1

    return int(agentAnswer)

def generateAnswer(figures, answers, pixelRatios):
    returnAnswer = None

    trend = computeTrends(figures)

    if 'trend' in trend:
        print('Trend is: ' + str(trend['trend']))

        # CASE 1: Each row is identical, so H? must be the same
        if trend['trend'] == 'identical rows':
            # Image._show(figures['H'])
            for answer in answers:
                newImg = ImageChops.logical_xor(figures['H'].convert("1"), answers[answer].convert("1"))
                # Image._show(newImg)
                ratios = getImageRatio(newImg)
                # print('Ratio for superimposition: ' + str(getImageRatio(out)))
                if 'white' in ratios:
                    if ratios['white'] <= 1000:
                        return answer

        # CASE 2: Diagonal similarity

        if trend['trend'] == 'diagonal':
            if 'value' in trend:
                if trend['value'] == 'same':
                    for answer in answers:
                        newImg = ImageChops.logical_xor(figures['E'].convert("1"), answers[answer].convert("1"))
                        # Image._show(newImg)
                        ratios = getImageRatio(newImg)
                        # print('ratios: ' + str(ratios))
                        if 'white' in ratios:
                            if ratios['white'] <= 1000:
                                return answer
                if trend['value'] == 'decrease':
                    if 'white' in trend and 'black' in trend:

                        # print('Trend = ' + str(trend))
                        blackVal = trend['black']
                        whiteVal = trend['white']
                        # Image._show(figures['A'])
                        # Image._show(figures['E'])

                        bestAnswer = None
                        lowestWhiteVal = 5000
                        for answer in answers:
                            newImg = ImageChops.logical_xor(figures['E'].convert("1"), answers[answer].convert("1"))
                            newImgRatio = getImageRatio(newImg)
                            # Image._show(newImg)
                            # print('New image ratio for answer ' + str(answer) +' = ' + str(newImgRatio))

                            if blackVal - 500 <= newImgRatio['black'] <= blackVal + 500 \
                                    and whiteVal - 500 <= newImgRatio['white'] <= whiteVal + 500:
                                        tempLow = newImgRatio['white']
                                        if tempLow < lowestWhiteVal:
                                            lowestWhiteVal = tempLow
                                            bestAnswer = answer
                                            # print('Best answer is: ' + str(bestAnswer))
                        return bestAnswer

                # if trend['value'] == 'increase':
                #     # print('Trend = ' + str(trend))
                #     if 'white' in trend and 'black' in trend:
                #         blackVal = trend['black']
                #         whiteVal = trend['white']
                #
                #         for answer in answers:
                #             newImg = ImageChops.logical_xor(figures['E'].convert("1"), answers[answer].convert("1"))
                #             newImgRatio = getImageRatio(newImg)
                #             # Image._show(newImg)
                #             # print('New image ratio for answer ' + str(answer) +' = ' + str(newImgRatio))
                #             if whiteVal - 550 <= newImgRatio['white'] <= whiteVal + 550:
                #                         return answer


        if trend['trend'] == 'column':
            CF = ImageChops.logical_xor(figures['C'].convert("1"), figures['F'].convert("1"))
            for answer in answers:
                FI = ImageChops.logical_xor(figures['F'].convert("1"), answers[answer].convert("1"))
                FIratio = getImageRatio(FI)
                CFI = ImageChops.logical_and(CF.convert("1"), FI.convert("1"))
                print('CFI ratio = ' + str(getImageRatio(CFI)))
                CFIratio = getImageRatio(CFI)

                # TODO: THIS SHIT GONNA NEED TO GET CHANGED
                if 'white' in CFIratio:
                    if CFIratio['white'] <= 1000:
                        return answer

    return returnAnswer


# Determine trends in the current matrix based on heuristics
# TODO: diagonal/column checks and confidence interval
def computeTrends(images):
    bestTrend = {}
    trendWeight = 0

    ABC = compareRow(images['A'], images['B'], images['C'])
    DEF = compareRow(images['D'], images['E'], images['F'])

    ADG = compareColumn(images['A'], images['D'], images['G'])
    BEH = compareColumn(images['B'], images['E'], images['H'])

    if 'result' in ABC and 'result' in DEF:
        # print('Result in ABC = ' + str(ABC) )
        # print('Result in DEF = ' + str(DEF))

        # TODO: will likely have to add weights
        # CASE 1: Images don't change in each row
        if ABC['result'] == 'same' and DEF['result'] == 'same':
            rowTrend = 100
            if trendWeight < rowTrend:
                trendWeight = rowTrend
                bestTrend.update({'trend': 'identical rows'})

        if ABC['result'] == 'different' and DEF['result'] == 'different':

            # CASE 3: Column check
            if 'result' in ADG and 'result' in BEH:
                if ADG['result'] == 'same' and BEH['result'] == 'same':
                    colTrend = 80
                    if trendWeight < colTrend:
                        trendWeight = colTrend
                        bestTrend.update({'trend': 'column'})

        if trendWeight < 50:
            # CASE 2: Check diagonal
            diagonal = checkDiagonal(images['A'], images['E'])
            if 'result' in diagonal:
                if diagonal['result'] == 'same':
                    bestTrend.update({'trend': 'diagonal', 'value': 'same'})
                if diagonal['result'] == 'decrease':
                    bestTrend.update({'trend': 'diagonal', 'value': 'decrease',
                                      'white': diagonal['white'], 'black': diagonal['black']})
                if diagonal['result'] == 'increase':
                    bestTrend.update({'trend': 'diagonal', 'value': 'increase',
                                      'white': diagonal['white'], 'black': diagonal['black']})

    return bestTrend


def checkDiagonal(img1, img2):
    result = {}
    newImg = ImageChops.logical_xor(img1.convert("1"), img2.convert("1"))

    img1Ratio = getImageRatio(img1)
    img2Ratio = getImageRatio(img2)
    newImgRatio = getImageRatio(newImg)

    # Image._show(img1)
    # Image._show(img2)
    # Image._show(newImg)
    #
    # print(img1Ratio)
    # print(img2Ratio)
    # print('Diagonal ratio:' + str(newImgRatio))


    if 'white' in newImgRatio and 'black' in img2Ratio and 'black' in img1Ratio:
        if newImgRatio['white'] <= 1000:
            result.update({'result': 'same'})
        else:
            # If xor white pixels + img2 black pixels equals img1 black pixels, DECREASE
            pixelSum = newImgRatio['white'] + img2Ratio['black']
            # print('pixel sum = ' + str(pixelSum))
            if pixelSum - 500 <= img1Ratio['black'] <= pixelSum + 500:
                result.update({'result': 'decrease', 'white': newImgRatio['white'], 'black': newImgRatio['black']})
            else:
                result.update({'result': 'increase', 'white': newImgRatio['white'], 'black': newImgRatio['black']})
    return result


def compareColumn(img1, img2, img3):
    results = {}
    # print('Column Testing...')

    AD = compareImages(img1, img2)
    DG = compareImages(img2, img3)


    if 'result' in AD and 'result' in DG:
        if AD['result'] and DG['result'] == 'same':
            results.update({'result': 'same'})
        else:
            newAD = ImageChops.logical_xor(img1.convert("1"), img2.convert("1"))
            newDG = ImageChops.logical_xor(img2.convert("1"), img3.convert("1"))
            ADG = ImageChops.logical_and(newAD.convert("1"), newDG.convert("1"))
            colRatio = getImageRatio(ADG)
            # print('Column ratio' + str(colRatio))
            if 'white' in colRatio:
                if colRatio['white'] <= 1000:
                    results.update({'result': 'same'})

    return results


# Compare images from L->R, top to bottom, or vice versa based on input order
def compareRow(img1, img2, img3):
    results = {}

    Image._show(ImageChops.logical_xor(img1.convert("1"), img2.convert("1")))

    AB = compareImages(img1, img2)
    BC = compareImages(img2, img3)

    if 'result' in AB and 'result' in BC:
        if AB['result'] and BC['result'] == 'same':
            results.update({'result': 'same'})
        else:
            results.update({'result': 'different'})

    return results


# Looks at two images values and returns properties
def compareImages(img1, img2):
    result = {}
    out = ImageChops.logical_xor(img1.convert("1"), img2.convert("1"))
    outRatio = getImageRatio(out)

    img1Ratios = getImageRatio(img1)
    img2Ratios = getImageRatio(img2)

    # diffRatio = getImageRatio(difference)
    # print('img2 ratios: ' + str(img2Ratios))
    # print('superimposed ratio: ' + str(outRatio))
    # print('difference ratios: ' + str(diffRatio))


    # Image._show(img1)
    # Image._show(img2)
    # Image._show(out)
    # print('imposition ratio: ' + str(outRatio))

    if outRatio['white'] <= 1000:
        result.update({'result': 'same'})
    else:
        result.update({'result': 'different', 'white': outRatio['white'], 'black': outRatio['black']})

    return result


# Returns a dictionary of PIL images associated with their given figure
def getImages(problem):
    images = {}

    for figure in problem.figures:
        fig = problem.figures[figure]
        figName = fig.name
        figImage = Image.open(fig.visualFilename)
        images.update({figName: figImage})

    return images


# Returns dictionary of image/pixel properties for SINGLE image
def getImageRatio(image):
    image.convert("1")
    ratios = {}
    imageAccess = image.load()

    whiteCount = 0
    blackCount = 0

    for i in range(0, image.size[0]):
        for j in range(0, image.size[1]):
            thisPixel = imageAccess[i, j]

            # If pixel is white, add to white values, else black values
            if image.mode == 'RGBA':
                if thisPixel == (255, 255, 255, 255):
                    whiteCount += 1
                else:
                    blackCount += 1
            else:
                if thisPixel == 0:
                    blackCount += 1
                else:
                    whiteCount += 1

    # Obtain ratio of black to white pixels in the image
    # print('white count = ' + str(whiteCount))
    # print('black count = ' + str(blackCount))
    try:
        ratio = float(blackCount) / whiteCount

    except ZeroDivisionError:
        ratio = 0.0

    ratios.update({'white': whiteCount, 'black': blackCount, 'ratio': ratio})
    return ratios


# Returns a dictionary of image/pixel properties for each figure
def getPixelRatios(images):
    pixelRatios = {}

    for img in images:
        # Get figure name
        figName = img[0]

        # Get PIL image for given figure
        image = images[figName]

        # Get PixelAccess class for image
        imageAccess = images[figName].load()

        whiteCount = 0
        blackCount = 0

        for i in range(0, image.size[0]):
            for j in range(0, image.size[1]):
                thisPixel = imageAccess[i, j]

                # If pixel is white, add to white values, else black values
                if thisPixel == (255, 255, 255, 255):
                    whiteCount += 1
                else:
                    blackCount += 1

        # Obtain ratio of black to white pixels in the image
        try:
            ratio = float(blackCount)/whiteCount

        except ZeroDivisionError:
            ratio = 0.0

        pixelRatios.update({figName:{'white':whiteCount,'black':blackCount,'ratio':ratio}})

    return pixelRatios


# Returns the ceiling of the number at 4 decimal places
def getCeil(value):
    return math.ceil(value*10000)/10000
