"""Learning content for 簡単に日本語を学ぶ - learn japanese easy (all checked, standard Japanese).
Markup: kanji run followed by [reading] = furigana; spaces separate words (for romaji) and are not shown.
(c)2026 EX Inc./HYPERION DIGITAL (c)2026"""

GOJUON = [  # rows of (kana, romaji); None = empty slot
    [("あ", "a"), ("い", "i"), ("う", "u"), ("え", "e"), ("お", "o")],
    [("か", "ka"), ("き", "ki"), ("く", "ku"), ("け", "ke"), ("こ", "ko")],
    [("さ", "sa"), ("し", "shi"), ("す", "su"), ("せ", "se"), ("そ", "so")],
    [("た", "ta"), ("ち", "chi"), ("つ", "tsu"), ("て", "te"), ("と", "to")],
    [("な", "na"), ("に", "ni"), ("ぬ", "nu"), ("ね", "ne"), ("の", "no")],
    [("は", "ha"), ("ひ", "hi"), ("ふ", "fu"), ("へ", "he"), ("ほ", "ho")],
    [("ま", "ma"), ("み", "mi"), ("む", "mu"), ("め", "me"), ("も", "mo")],
    [("や", "ya"), None, ("ゆ", "yu"), None, ("よ", "yo")],
    [("ら", "ra"), ("り", "ri"), ("る", "ru"), ("れ", "re"), ("ろ", "ro")],
    [("わ", "wa"), None, None, None, ("を", "wo / o")],
    [("ん", "n"), None, None, None, None],
]


def kata(s):
    return "".join(chr(ord(c) + 0x60) if "\u3041" <= c <= "\u3096" else c for c in s)


# category, markup, romaji, English
WORDS = [
    ("Greetings", "あいさつ", [
        ("こんにちは", "konnichiwa", "Hello / Good afternoon"),
        ("おはよう ございます", "ohayō gozaimasu", "Good morning"),
        ("こんばんは", "konbanwa", "Good evening"),
        ("ありがとう ございます", "arigatō gozaimasu", "Thank you"),
        ("すみません", "sumimasen", "Excuse me / Sorry"),
        ("さようなら", "sayōnara", "Goodbye"),
        ("はい", "hai", "Yes"),
        ("いいえ", "iie", "No"),
        ("お願[ねが]い します", "onegai shimasu", "Please"),
        ("いただきます", "itadakimasu", "Said before eating"),
    ]),
    ("Numbers 1-10", "かず", [
        ("一[いち]", "ichi", "1  one"), ("二[に]", "ni", "2  two"), ("三[さん]", "san", "3  three"),
        ("四[よん]", "yon  (also shi)", "4  four"), ("五[ご]", "go", "5  five"), ("六[ろく]", "roku", "6  six"),
        ("七[なな]", "nana  (also shichi)", "7  seven"), ("八[はち]", "hachi", "8  eight"),
        ("九[きゅう]", "kyū  (also ku)", "9  nine"), ("十[じゅう]", "jū", "10  ten"),
    ]),
    ("Food", "たべもの", [
        ("ご飯[はん]", "gohan", "Rice / a meal"), ("水[みず]", "mizu", "Water"), ("お茶[ちゃ]", "ocha", "Green tea"),
        ("魚[さかな]", "sakana", "Fish"), ("肉[にく]", "niku", "Meat"), ("寿司[すし]", "sushi", "Sushi"),
        ("野菜[やさい]", "yasai", "Vegetables"), ("果物[くだもの]", "kudamono", "Fruit"), ("パン", "pan", "Bread"),
        ("卵[たまご]", "tamago", "Egg"),
    ]),
    ("Family", "かぞく", [
        ("家族[かぞく]", "kazoku", "Family"), ("父[ちち]", "chichi", "(my) father"), ("母[はは]", "haha", "(my) mother"),
        ("兄[あに]", "ani", "(my) older brother"), ("姉[あね]", "ane", "(my) older sister"),
        ("弟[おとうと]", "otōto", "(my) younger brother"), ("妹[いもうと]", "imōto", "(my) younger sister"),
        ("友達[ともだち]", "tomodachi", "Friend"), ("子供[こども]", "kodomo", "Child"), ("先生[せんせい]", "sensei", "Teacher"),
    ]),
]

# beginner kanji: kanji, readings (kun・ON), English
KANJI = [
    ("一", "ひと・イチ", "one"), ("二", "ふた・ニ", "two"), ("三", "み・サン", "three"), ("十", "とお・ジュウ", "ten"),
    ("日", "ひ・ニチ", "sun, day"), ("月", "つき・ゲツ", "moon, month"), ("火", "ひ・カ", "fire"), ("水", "みず・スイ", "water"),
    ("木", "き・モク", "tree"), ("金", "かね・キン", "gold, money"), ("土", "つち・ド", "soil, earth"), ("山", "やま・サン", "mountain"),
    ("川", "かわ・セン", "river"), ("人", "ひと・ジン", "person"), ("口", "くち・コウ", "mouth"), ("大", "おお・ダイ", "big"),
    ("小", "ちい・ショウ", "small"), ("上", "うえ・ジョウ", "up, above"), ("下", "した・カ", "down, below"), ("学", "まな・ガク", "study"),
    ("生", "い・セイ", "life, birth"), ("先", "さき・セン", "ahead, before"), ("年", "とし・ネン", "year"), ("本", "もと・ホン", "book, origin"),
]
KANJI_WORDS = [("日本[にほん]", "nihon", "Japan"), ("日本語[にほんご]", "nihongo", "Japanese language"),
               ("学生[がくせい]", "gakusei", "student"), ("先生[せんせい]", "sensei", "teacher"), ("大学[だいがく]", "daigaku", "university")]

# ---------------------------------------------------------------------------- offline translator data
NOUNS = {
    "japan": "日本[にほん]", "japanese": "日本語[にほんご]", "japanese language": "日本語[にほんご]", "teacher": "先生[せんせい]",
    "student": "学生[がくせい]", "friend": "友達[ともだち]", "friends": "友達[ともだち]", "school": "学校[がっこう]", "book": "本[ほん]",
    "cat": "猫[ねこ]", "dog": "犬[いぬ]", "water": "水[みず]", "tea": "お茶[ちゃ]", "green tea": "お茶[ちゃ]", "coffee": "コーヒー",
    "sushi": "寿司[すし]", "ramen": "ラーメン", "rice": "ご飯[はん]", "fish": "魚[さかな]", "meat": "肉[にく]", "family": "家族[かぞく]",
    "mother": "お母[かあ]さん", "mom": "お母[かあ]さん", "father": "お父[とう]さん", "dad": "お父[とう]さん", "mountain": "山[やま]",
    "river": "川[かわ]", "sea": "海[うみ]", "ocean": "海[うみ]", "sky": "空[そら]", "flower": "花[はな]", "flowers": "花[はな]",
    "tree": "木[き]", "sun": "太陽[たいよう]", "moon": "月[つき]", "station": "駅[えき]", "train": "電車[でんしゃ]", "car": "車[くるま]",
    "house": "家[いえ]", "home": "家[いえ]", "toilet": "トイレ", "bathroom": "トイレ", "hotel": "ホテル", "music": "音楽[おんがく]",
    "movie": "映画[えいが]", "movies": "映画[えいが]", "anime": "アニメ", "manga": "漫画[まんが]", "tokyo": "東京[とうきょう]",
    "kyoto": "京都[きょうと]", "osaka": "大阪[おおさか]", "mount fuji": "富士山[ふじさん]", "fuji": "富士山[ふじさん]", "summer": "夏[なつ]",
    "winter": "冬[ふゆ]", "spring": "春[はる]", "autumn": "秋[あき]", "fall": "秋[あき]", "today": "今日[きょう]", "tomorrow": "明日[あした]",
    "yesterday": "昨日[きのう]", "morning": "朝[あさ]", "night": "夜[よる]", "money": "お金[かね]", "time": "時間[じかん]",
    "love": "愛[あい]", "heart": "心[こころ]", "dream": "夢[ゆめ]", "person": "人[ひと]", "people": "人[ひと]たち", "child": "子供[こども]",
    "children": "子供[こども]たち", "name": "名前[なまえ]", "phone": "電話[でんわ]", "game": "ゲーム", "games": "ゲーム", "bread": "パン",
    "egg": "卵[たまご]", "fruit": "果物[くだもの]", "apple": "りんご", "cake": "ケーキ", "beer": "ビール", "milk": "牛乳[ぎゅうにゅう]",
    "rain": "雨[あめ]", "snow": "雪[ゆき]", "wind": "風[かぜ]", "fire": "火[ひ]", "cherry blossom": "桜[さくら]",
    "cherry blossoms": "桜[さくら]", "sakura": "桜[さくら]", "kimono": "着物[きもの]", "ninja": "忍者[にんじゃ]", "samurai": "侍[さむらい]",
    "dragon": "竜[りゅう]", "art": "芸術[げいじゅつ]", "language": "言葉[ことば]", "word": "言葉[ことば]", "town": "町[まち]",
    "city": "町[まち]", "country": "国[くに]", "world": "世界[せかい]", "everyone": "皆[みな]さん", "everybody": "皆[みな]さん",
    "brother": "兄弟[きょうだい]", "sister": "姉妹[しまい]", "baby": "赤[あか]ちゃん", "girl": "女[おんな]の 子[こ]", "boy": "男[おとこ]の 子[こ]",
    "woman": "女[おんな]の 人[ひと]", "man": "男[おとこ]の 人[ひと]", "umbrella": "傘[かさ]", "parasol": "日傘[ひがさ]",
    "you": "あなた", "me": "私[わたし]", "i": "私[わたし]", "this": "これ", "that": "それ", "here": "ここ", "there": "そこ",
    "vegetables": "野菜[やさい]", "food": "食[た]べ物[もの]", "breakfast": "朝[あさ]ご飯[はん]", "lunch": "昼[ひる]ご飯[はん]",
    "dinner": "晩[ばん]ご飯[はん]", "shop": "店[みせ]", "store": "店[みせ]", "restaurant": "レストラン", "park": "公園[こうえん]",
    "temple": "お寺[てら]", "shrine": "神社[じんじゃ]", "castle": "城[しろ]", "bird": "鳥[とり]", "horse": "馬[うま]",
}
ADJ = {
    "beautiful": "きれい", "pretty": "きれい", "big": "大[おお]きい", "small": "小[ちい]さい", "delicious": "おいしい", "tasty": "おいしい",
    "cute": "かわいい", "fun": "楽[たの]しい", "hot": "暑[あつ]い", "cold": "寒[さむ]い", "good": "いい", "happy": "嬉[うれ]しい",
    "new": "新[あたら]しい", "old": "古[ふる]い", "expensive": "高[たか]い", "cheap": "安[やす]い", "easy": "簡単[かんたん]",
    "difficult": "難[むずか]しい", "hard": "難[むずか]しい", "interesting": "面白[おもしろ]い", "cool": "かっこいい", "red": "赤[あか]い",
    "blue": "青[あお]い", "white": "白[しろ]い", "black": "黒[くろ]い", "fast": "速[はや]い", "quiet": "静[しず]か", "kind": "親切[しんせつ]",
    "tired": "疲[つか]れた", "busy": "忙[いそが]しい", "strong": "強[つよ]い",
}
NA_ADJ = {"きれい", "簡単[かんたん]", "静[しず]か", "親切[しんせつ]"}       # take な before a noun
PHRASES = {
    "hello": "こんにちは", "hi": "こんにちは", "good afternoon": "こんにちは", "good morning": "おはよう ございます",
    "good evening": "こんばんは", "good night": "おやすみ なさい", "goodbye": "さようなら", "bye": "さようなら",
    "see you": "また ね", "see you later": "また あとで", "see you tomorrow": "また 明日[あした]", "thank you": "ありがとう ございます",
    "thanks": "ありがとう", "thank you very much": "どうも ありがとう ございます", "sorry": "ごめん なさい", "i'm sorry": "ごめん なさい",
    "i am sorry": "ごめん なさい", "excuse me": "すみません", "please": "お願[ねが]い します", "yes": "はい", "no": "いいえ",
    "nice to meet you": "はじめまして", "how are you": "お元気[げんき] です か", "i'm fine": "元気[げんき] です", "i am fine": "元気[げんき] です",
    "welcome": "ようこそ", "cheers": "乾杯[かんぱい]", "let's eat": "いただきます", "thanks for the meal": "ごちそうさま でした",
    "i understand": "分[わ]かります", "i don't understand": "分[わ]かりません", "i do not understand": "分[わ]かりません",
    "what is this": "これ は 何[なん] です か", "how much is this": "これ は いくら です か", "how much": "いくら です か",
    "i love you": "愛[あい]して います", "i am a student": "私[わたし] は 学生[がくせい] です",
    "i am studying japanese": "日本語[にほんご] を 勉強[べんきょう] して います", "i study japanese": "日本語[にほんご] を 勉強[べんきょう] します",
    "happy birthday": "お誕生日[たんじょうび] おめでとう ございます", "congratulations": "おめでとう ございます",
    "welcome to japan": "日本[にほん] へ ようこそ", "learn japanese easy": "簡単[かんたん] に 日本語[にほんご] を 学[まな]ぶ",
    "i'm hungry": "お腹[なか] が すきました", "i am hungry": "お腹[なか] が すきました", "good luck": "頑張[がんば]って",
    "do your best": "頑張[がんば]って", "it's delicious": "おいしい です", "delicious": "おいしい", "i'm home": "ただいま",
    "welcome home": "お帰[かえ]り なさい", "i'm leaving": "行[い]って きます", "have a nice day": "いい 一日[いちにち] を",
    "do you speak english": "英語[えいご] を 話[はな]せます か", "i speak a little japanese": "日本語[にほんご] を 少[すこ]し 話[はな]せます",
    "what is your name": "お名前[なまえ] は 何[なん] です か", "where are you from": "どこ から 来[き]ました か",
    "i am from england": "イギリス から 来[き]ました", "i am from america": "アメリカ から 来[き]ました", "help": "助[たす]けて",
    "wait": "待[ま]って", "wait a moment": "ちょっと 待[ま]って ください", "i love japan": "日本[にほん] が 大好[だいす]き です",
    "good morning teacher": "先生[せんせい] 、 おはよう ございます",
}
GREETINGS = {"good morning": "おはよう ございます", "hello": "こんにちは", "hi": "こんにちは", "good evening": "こんばんは",
             "good night": "おやすみ なさい", "goodbye": "さようなら", "thank you": "ありがとう ございます", "thanks": "ありがとう"}
