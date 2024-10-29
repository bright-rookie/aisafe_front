import numpy as np


def run_ai_analysis(info, bruise, response, lab, xray, video):
    abuse = False
    if (
        response[0] == 1 or
        response[2] == 0 or
        response[3] == 1 or
        response[4] == 0 or
        response[5] == 0 or
        response[6] == 1 or
        response[7] == 0 or
        response[8] == 0
    ) :
        poss = round(np.random.uniform(0.5, 1), 2)
        return poss, [('문진 정보', round(poss*2/3, 2)), ('멍 정보', round(poss*1/6, 2)), ('영상', round(poss/10, 2)), ('Lab 결과', round(poss/30, 2)), ('X-ray', round(poss/30, 2)) ]
    else :
        poss = round(np.random.uniform(0, 0.5), 2)
        return poss, [('문진 정보', round(poss*2/3, 2)), ('멍 정보', round(poss*1/6, 2)), ('영상', round(poss/10, 2)), ('Lab 결과', round(poss/30, 2)), ('X-ray', round(poss/30, 2)) ]
