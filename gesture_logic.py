def fingers_up(lmList):
    """
    Returns [thumb, index, middle, ring, pinky]
    1 = up, 0 = down
    """

    tips = [4, 8, 12, 16, 20]
    fingers = []

    # ---------- Thumb ----------
    # Compare thumb tip X with previous joint X
    if lmList[4][1] > lmList[3][1]:
        fingers.append(1)
    else:
        fingers.append(0)

    # ---------- Other 4 fingers ----------
    for i in range(1, 5):
        # If tip is higher (smaller y) than pip joint -> finger is up
        if lmList[tips[i]][2] < lmList[tips[i] - 2][2]:
            fingers.append(1)
        else:
            fingers.append(0)

    return fingers

def is_palm_facing_camera(lmList):
    """
    Robust palm-facing detection using 2D geometry.
    Works reliably on webcams.
    """

    # MCP joints of index and pinky
    index_mcp = lmList[5]
    pinky_mcp = lmList[17]

    # Fingertips
    index_tip = lmList[8]
    pinky_tip = lmList[20]

    # Palm width (spread of hand)
    palm_width = abs(index_mcp[1] - pinky_mcp[1])

    # Finger spread at tips
    tip_spread = abs(index_tip[1] - pinky_tip[1])

    # Palm facing camera → fingers spread wider than base
    return tip_spread > palm_width * 0.85


def classify_gesture(f, lmList=None):
    """
    f = [thumb, index, middle, ring, pinky]
    """

    # ---------------- Basic Gestures ----------------

    # FIST
    if f == [0,0,0,0,0]:
        return "FIST"

    # OPEN
    # OPEN (front palm only)
    if f == [1,1,1,1,1] and is_palm_facing_camera(lmList):
        return "OPEN"


    # V SIGN
    if f[1] == 1 and f[2] == 1 and f[3] == 0 and f[4] == 0:
        return "V_SIGN"

    # THUMBS UP
    if f == [1,0,0,0,0]:
        # Check thumb is actually above wrist
        if lmList and lmList[4][2] < lmList[0][2]:
            return "THUMBS_UP"

    # THUMBS DOWN
    if f == [1,0,0,0,0]:
        # Check thumb is below wrist
        if lmList and lmList[4][2] > lmList[0][2]:
            return "THUMBS_DOWN"

    # ---------------- Single Finger Gestures ----------------

    # INDEX
    if f == [0,1,0,0,0]:
        return "INDEX"

    # MIDDLE
    if f == [0,0,1,0,0]:
        return "MIDDLE"

    # RING
    if f == [0,0,0,1,0]:
        return "RING"

    # PINKY
    if f == [0,0,0,0,1]:
        return "PINKY"

    return "UNKNOWN"
