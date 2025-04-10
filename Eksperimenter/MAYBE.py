import math

# Constants
VERY_BIG = 1e10  # A very large number
MID = 0.5
SIDE = 0.5
ALPHA = 0.1
MAX_RUN = 1000
MAXLENGTH = 10000
NEW_ROW = 1
NEW_COL = 2
NEW_BOTH = 3

# Global variables
fsize = 0
bsize = 0
params = 0
ysize = 0
t = 0
h = 0
runCount = 0
iter = 0
score_loaded = False
x = []
y = []
Dist = []
dtw = []
history = []
previous = 0
top_weight = SIDE
bot_weight = SIDE
mid_weight = MID
b_dtw = []
b_move = []
b_err = []
b_start = 0
bh_start = 0
t_mod = 0
h_mod = 0
m_iter = 0
m_ideal_iter = 0


def set_score_size(v):
    global y, score_loaded, iter, ysize
    if v < MAXLENGTH and v > bsize:
        iter = 0
        score_loaded = False
        ysize = v

        y.clear()
        y.extend([[0] * params for _ in range(ysize)])

        start()  # Call the start function to reset necessary structures
        history.clear()
        history.extend([0] * (ysize * 3))  # Leave room for t be 3 times longer than h

        return ysize
    return 0


def process_score_fv(tfeat):
    global iter, y, score_loaded
    if iter < ysize:
        for j in range(params):
            y[iter][j] = tfeat[j]
        iter += 1

    if iter == ysize:
        score_loaded = True

    return iter


def process_live_fv(tfeat):
    global t, h, x
    if t == 0:
        init_dtw()
    else:
        for i in range(params):
            x[t % bsize][i] = tfeat[i]

        if dtw_process():  # Compute DTW path until we reach h == ysize


def start():
    global t, h, runCount, previous, x, Dist, dtw, history, b_dtw, b_move, b_err, b_start, bh_start, t_mod, h_mod
    t = h = runCount = m_iter = m_ideal_iter = 0
    b_start = bh_start = 0
    previous = 0

    x.clear()
    x.extend([[0] * params for _ in range(bsize)])

    Dist.clear()
    Dist.extend([[0] * bsize for _ in range(bsize)])

    dtw.clear()
    dtw.extend([[VERY_BIG] * fsize for _ in range(fsize)])

    history.clear()
    history.extend([0] * (ysize * 3))

    b_dtw.clear()
    b_dtw.extend([[VERY_BIG] * bsize for _ in range(bsize)])

    b_move.clear()
    b_move.extend([[0] * bsize for _ in range(bsize)])

    b_err.clear()
    b_err.extend([[0] * 4 for _ in range(bsize)])


def get_t():
    return t

def get_h():
    return h

def set_h(to_h):
    global h, h_mod
    h = to_h
    h_mod = h % fsize

def get_run_count():
    return runCount

def get_history(from_t):
    return history[from_t]

def get_y(i, j):
    return y[i][j]

def get_fsize():
    return fsize

def get_bsize():
    return bsize

def get_back_path():
    return b_err

def is_running():
    return h < ysize and h > 0

def is_score_loaded():
    return score_loaded

def set_params(params_):
    global params
    if params_ != params:
        params = params_
        start()

def init_dtw():
    distance(t, h)
    for i in range(fsize):
        for j in range(fsize):
            dtw[i][j] = VERY_BIG
    dtw[t_mod][h_mod] = Dist[t % bsize][h % bsize]  # Initial starting point
    increment_t()
    increment_h()
    history[1] = 1

def distance(i, j):
    global Dist
    imod = i % bsize
    jmod = j % bsize
    total = 0
    if x[imod][0] == 0 or y[j][0] == 0:
        total = VERY_BIG
    else:
        for k in range(params):
            total += (x[imod][k] - y[j][k]) ** 2

    if total < 0.0001:
        total = 0
    total = math.sqrt(total)
    total += ALPHA

    Dist[imod][jmod] = total

def get_inc():
    global dtw, t_mod, h_mod
    min_val = VERY_BIG
    next_inc = 0
    tmin1 = (t_mod + fsize - 1) % fsize
    hmin1 = (h_mod + fsize - 1) % fsize

    for i in range(fsize):
        if dtw[i][hmin1] < min_val:
            min_val = dtw[i][hmin1]
            next_inc = NEW_ROW

    for i in range(fsize):
        if dtw[tmin1][i] <= min_val:
            min_val = dtw[tmin1][i]
            next_inc = NEW_COL

    if dtw[tmin1][hmin1] <= min_val:
        next_inc = NEW_BOTH

    return next_inc

def calc_dtw(i, j):
    global dtw, Dist
    imin1 = (i + fsize - 1) % fsize
    imin2 = (i + fsize - 2) % fsize
    jmin1 = (j + fsize - 1) % fsize
    jmin2 = (j + fsize - 2) % fsize

    top = dtw[imin2][jmin1] + Dist[i % bsize][j % bsize] * top_weight
    mid = dtw[imin1][jmin1] + Dist[i % bsize][j % bsize] * mid_weight
    bot = dtw[imin1][jmin2] + Dist[i % bsize][j % bsize] * bot_weight

    cheapest = min(top, mid, bot)
    dtw[i % fsize][j % fsize] = cheapest

def dtw_process():
    global t, h, history, runCount, previous
    inc = get_inc()
    jstart = 0

    while inc == NEW_ROW and h < ysize:
        if t < bsize:
            jstart = 0
        else:
            jstart = t - bsize

        for j in range(jstart, t):
            distance(j, h)
            calc_dtw(j, h)

        increment_h()
        previous = NEW_ROW
        runCount += 1
        inc = get_inc()

    if h < ysize:
        if inc != NEW_ROW:
            jstart = 0 if h < bsize else h - bsize
            for j in range(jstart, h):
                distance(t, j)
                calc_dtw(t, j)
            increment_t()

        if inc != NEW_COL:
            jstart = 0 if t < bsize else t - bsize
            for j in range(jstart, t):
                distance(j, h)
                calc_dtw(j, h)
            increment_h()

        if inc == previous:
            runCount += 1
        else:
            runCount = 1
        if inc != NEW_BOTH:
            previous = inc

        history[t] = h
        return True

    increment_t()
    history[t] = h
    return False


def increment_t():
    global t, t_mod
    t += 1
    t_mod = (t_mod + 1) % fsize


def increment_h():
    global h, h_mod
    h += 1
    h_mod = (h_mod + 1) % fsize
