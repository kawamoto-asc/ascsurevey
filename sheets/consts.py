# シート 入力形式
INPUT_TYPE_CHOICES = (
    (1, '1:一問一答'),
    (2, '2:一問多答'),
)

# 項目入力タイプ
FIELD_TYPE_CHOICES = (
    ('select', 'select'),
    ('textarea', 'textarea'),
)

# 集計タイプ
AGGRE_TYPE_CHOICES = (
    (0, '0:集計なし'),
    (1, '1:集計あり'),
)

# アンケート入力画面URL
INPUT_URL = '/ascsurvey/input/'

# アンケート集計画面URL
AGGRE_URL = '/ascsurvey/aggregate/'
