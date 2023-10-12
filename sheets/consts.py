# シート 入力形式
INPUT_TYPE_CHOICES = (
    (1, '1:一問一答採点'),
    (2, '2:一問多答'),
)

# 項目入力タイプ
FIELD_TYPE_CHOICES = (
    ('SELECT_CHOICES01', '〇×入力形式'),
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
SUM_URL = '/ascsurvey/summarize/'

# 入力項目
SELECT_CHOICES01 = (
    ('〇', '〇'),
    ('×', '×'),
)