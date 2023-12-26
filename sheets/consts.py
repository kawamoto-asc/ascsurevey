# シート 入力形式
INPUT_TYPE_CHOICES = (
    (1, '1:一問一答採点'),
    (2, '2:一問多答'),
    (3, '3:チャレンジ評価(部署別)'),
)

# 項目入力タイプ
FIELD_TYPE_CHOICES = (
    ('SELECT_CHOICES01', '〇×入力形式'),
    ('SELECT_CHOICES02', '5段階入力形式(S-C,未提出)'),
    ('SELECT_CHOICES03', '順位選択形式(1-5位)'),
    ('textarea', 'textarea'),
)

# 集計タイプ
AGGRE_TYPE_CHOICES = (
    (0, '0:集計なし'),
    (1, '1:集計あり'),
)

# アンケート入力画面URL
INPUT_URL = '/ascsurvey/input/'

# アンケート集約画面URL
SUM_URL = '/summarize/'

# 集約画面サブタイトル
MSUM_STR = '照会'

# 入力項目
SELECT_CHOICES01 = (
    ('〇', '〇'),
    ('×', '×'),
)

SELECT_CHOICES02 = (
    ('S', 'S'),
    ('A', 'A'),
    ('B', 'B'),
    ('C', 'C'),
    ('未提出', '未提出'),
)

SELECT_CHOICES03 = (
    ('1', '1位'),
    ('2', '2位'),
    ('3', '3位'),
    ('4', '4位'),
    ('5', '5位'),
)
