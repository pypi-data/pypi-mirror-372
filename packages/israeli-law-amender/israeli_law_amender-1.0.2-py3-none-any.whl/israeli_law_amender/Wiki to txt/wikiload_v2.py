import requests
from bs4 import BeautifulSoup
import urllib.parse
import os
import time
import re

# --- Configuration ---
BASE_URL = "https://he.wikisource.org"
WIKI_PAGE_URL_FORMAT = BASE_URL + "/wiki/{}" # For initial lookup
INDEX_PHP_URL_FORMAT_RAW_BY_TITLE = BASE_URL + "/w/index.php?title={}&action=raw" # For current content by title
INDEX_PHP_URL_FORMAT_HISTORY = BASE_URL + "/w/index.php?title={}&action=history&dir=prev&limit=500"
INDEX_PHP_URL_FORMAT_OLDID_RAW = BASE_URL + "/w/index.php?title={}&oldid={}&action=raw" # For specific oldid
OUTPUT_DIR = "Data/wikitext_laws"
REQUEST_DELAY_SECONDS = 1.5 # Being polite
MAX_WIKITEXT_REDIRECT_HOPS_FOR_CURRENT = 3 # How many wikitext redirects to follow for current version
MAX_ORIGINAL_VERSION_ATTEMPTS = 3 # How many oldest versions to check for non-stub/non-redirect

law_names_no_dates_input = [
    'חוק הפיקוח על שירותים פיננסיים (שירותים פיננסיים מוסדרים)',
    'חוק רישוי שירותים ומקצועות בענף הרכב',
    'חוק סמכויות מיוחדות להתמודדות עם נגיף הקורונה החדש (הוראת שעה)',
    'חוק המאבק בטרור',
    'חוק ההתייעלות הכלכלית (תיקוני חקיקה להשגת יעדי התקציב לשנות התקציב 2017 ו-2018)',
    'חוק חדלות פירעון ושיקום כלכלי',
    'חוק המידע הפלילי ותקנת השבים',
    'חוק התכנית לסיוע כלכלי (נגיף הקורונה החדש) (הוראת שעה)',
    'חוק ההתייעלות הכלכלית (תיקוני חקיקה להשגת יעדי התקציב לשנות התקציב 2015 ו-2016)',
    'חוק אומנה לילדים',
    'חוק שירות אזרחי',
    'חוק פנייה לגופים ציבוריים באמצעי קשר דיגיטליים',
    'חוק התכנית הכלכלית (תיקוני חקיקה ליישום המדיניות הכלכלית לשנות התקציב 2021 ו-2022)',
    'חוק נתוני אשראי',
    'חוק להגברת התחרות ולצמצום הריכוזיות בשוק הבנקאות בישראל (תיקוני חקיקה)',
    'חוק הרשות הממשלתית להתחדשות עירונית',
    'חוק גיל פרישה (הורה שילדו נפטר) (הוראת שעה)',
    'חוק הפיקוח על מעונות יום לפעוטות',
    'חוק מענק לעידוד תעסוקה (הוראת שעה – נגיף הקורונה החדש)',
    'חוק קיום דיונים בהיוועדות חזותית בהשתתפות עצורים, אסירים וכלואים בתקופת התפשטות נגיף הקורונה החדש (הוראת שעה)',
    'חוק הרשות למאבק באלימות, בסמים ובאלכוהול',
    'חוק לפיקוח על איכות המזון ולתזונה נכונה בצהרונים',
    'חוק תיירות מרפא',
    'חוק למניעת הטרדות של מוקדי חירום',
    'חוק חסימת מספר טלפון לשם מניעת ביצוע עבירות',
    'חוק מענק הסתגלות מיוחד לבני 67 ומעלה (הוראת שעה – נגיף הקורונה החדש)',
    'חוק שירותי תשלום',
    'חוק הסמכת צבא הגנה לישראל ושירות הביטחון הכללי לביצוע חדירה לחומר מחשב המשמש להפעלת מצלמה נייחת ופעולה בו (הוראת שעה – חרבות ברזל)',
    'חוק תגמולים לבני משפחה של חטופים ונעדרים בפעולת איבה',
    'חוק סליקה אלקטרונית של שיקים',
    'חוק התחדשות עירונית (הסכמים לארגון עסקאות)',
    'חוק לייעול הפיקוח והאכיפה העירוניים ברשויות המקומיות (תעבורה)',
    'חוק סמכויות לאיסוף ואבחון של נתוני נוסעים הנכנסים לישראל או היוצאים ממנה',
    'חוק התוכנית הכלכלית (תיקוני חקיקה ליישום המדיניות הכלכלית לשנות התקציב 2023 ו-2024)',
    'חוק החזקת תכשיר אפינפרין במוסדות חינוך ובמקומות ציבוריים',
    'חוק סמכויות לשם מניעת ביצוע עבירות באמצעות אתר אינטרנט',
    'חוק לצמצום השימוש בשקיות נשיאה חד-פעמיות',
    'חוק ההתייעלות הכלכלית (תיקוני חקיקה להשגת יעדי התקציב לשנת התקציב 2019)',
    'חוק האזרחות והכניסה לישראל (הוראת שעה)',
    'חוק לדחיית הבחירות הכלליות לרשויות המקומיות',
    'חוק הגבלות על משך השעיה של עובד גוף ציבורי עקב הליכים פליליים',
    'חוק הרבנות הראשית לישראל (הארכת כהונה של הרבנים הראשיים לישראל ושל חברי מועצת הרבנות הראשית לישראל) (הוראת שעה)',
    'חוק הגז הפחמימני המעובה',
    'חוק מניעת פגיעת גוף שידורים זר בביטחון המדינה (הוראת שעה – חרבות ברזל)',
    'חוק התמודדות עם תקיפות סייבר חמורות במגזר השירותים הדיגיטליים ושירותי האחסון (הוראת שעה - חרבות ברזל)',
    'חוק לצמצום השימוש במזומן',
    'חוק תקציב המדינה לשנים 2017 ו-2018 (הוראות מיוחדות) (הוראת שעה)',
    'חוק שדה התעופה דב הוז (הוראות מיוחדות)',
    'חוק הארכת תקופות ודחיית מועדים בענייני הליכי מס ומענקי סיוע (נגיף הקורונה החדש – הוראת שעה – תיקוני חקיקה)',
    'חוק הסמכת שירות הביטחון הכללי לסייע במאמץ הלאומי לצמצום התפשטות נגיף הקורונה החדש (הוראת שעה)',
    'חוק התכנית לסיוע כלכלי (נגיף הקורונה החדש – מענק חד-פעמי) (הוראת שעה ותיקוני חקיקה)',
    'חוק הארכת תקופות (הוראת שעה – נגיף הקורונה החדש) (אישורים רגולטוריים)',
    'חוק הבחירות לכנסת העשרים וארבע (הוראות מיוחדות ותיקוני חקיקה)',
    'חוק דחיית מועדים לביצוע בדיקות של מיתקני גז (נגיף הקורונה החדש) (הוראת שעה)',
    'חוק המועצה לגיל הרך',
    'חוק הסדרת העיסוק בהדברה תברואית',
    'חוק מוסר תשלומים לספקים',
    'חוק הפיקוח על מחירי קייטנות ציבוריות',
    'חוק לפיקוח על הפעלת צהרונים',
    'חוק להסדרת מתן שירותי פיקדון ואשראי בלא ריבית על ידי מוסדות לגמילות חסדים',
    'חוק עידוד תרומות מזון',
    'חוק איסור פרסום מידע לגבי נפגעים',
    'חוק ההתייעלות הכלכלית (תיקוני חקיקה להשגת יעדי התקציב לשנות התקציב 2021 ו-2022)',
    'חוק הארכת תקופות ודחיית מועדים (הוראת שעה – חרבות ברזל) (סדרי מינהל, תקופות כהונה ותאגידים)',
    'חוק התקנת מצלמות לשם הגנה על פעוטות במעונות יום לפעוטות',
    'חוק עידוד מעורבות סטודנטים בפעילות חברתית וקהילתית',
    'חוק ניוד מידע רפואי',
    'חוק התוכנית לסיוע כלכלי (הוראת שעה – חרבות ברזל)',
    'חוק קיום דיונים בהיוועדות חזותית בהשתתפות עצורים ואסירים (הוראת שעה – חרבות ברזל)',
    'חוק התקציב לשנת הכספים 2023',
    'חוק דחיית מועדים (הוראת שעה – חרבות ברזל) (חוזה, פסק דין או תשלום לרשות)',
    'חוק שירותי רווחה לאנשים עם מוגבלות',
    'חוק למניעת העסקה במוסדות מסוימים של מי שהורשע באלימות כלפי ילדים וחסרי ישע',
    'חוק התקציב לשנת הכספים 2024',
    'חוק תקציב נוסף לשנת הכספים 2024',
    'חוק תקציב נוסף לשנת הכספים 2024 (מס\' 2)',
    'חוק הקפאה והפחתה של דמי הבראה בשנת 2024 לשם תקצוב הטבות לחיילי מילואים',
    'חוק המכון הלאומי למצוינות בספורט (מכון וינגייט)',
    'חוק הגנה על זכויות אמנים במוסיקה',
    'חוק תגמול לנושאי משרה בתאגידים פיננסיים (אישור מיוחד ואי-התרת הוצאה לצורכי מס בשל תגמול חריג)',
    'חוק שירות הציבור (הצהרת הון)',
    'חוק-יסוד: ישראל – מדינת הלאום של העם היהודי',
    'חוק יום העלייה',
    'חוק העיצובים',
    'חוק הכרה אזרחית בהכשרות צבאיות',
    'חוק התקציב לשנות התקציב 2015 ו-2016',
    'חוק קרן קיימת לישראל (תחולת דיני המס והוראת שעה)',
    'חוק אמנת הבנק האסייני להשקעות בתשתיות',
    'חוק הוקרה לאזרחים במערכות ישראל',
    'חוק תעריפי התחבורה הציבורית',
    'חוק הגנה על בתי עסק (ימי המנוחה)',
    'חוק נציבות תלונות הציבור על מייצגי המדינה בערכאות',
    'חוק הקלה באמצעי משמעת המוטלים על בעלי מקצועות מוסדרים',
    'חוק-יסוד: תקציב המדינה לשנים 2017 ו-2018 (הוראות מיוחדות) (הוראת שעה)',
    'חוק הפחתת תוספות פיגור שנוספו על קנסות הנגבים בידי המרכז לגביית קנסות, אגרות והוצאות (הוראת שעה)',
    'חוק סיוע כלכלי לעידוד לומדי תורה וסטודנטים נזקקים',
    'חוק לעידוד השקעה באנרגיות מתחדשות (הטבות מס בשל הפקת חשמל מאנרגיה מתחדשת)',
    'חוק התקציב לשנות הכספים 2017 ו-2018',
    'חוק תשתיות להולכה ולאחסון של נפט על ידי גורם מפעיל',
    'חוק להסדרת ההתיישבות ביהודה והשומרון',
    'חוק להקלת נטל האסדרה בעסקים (איחוד שילוט)',
    'חוק להקפאת כספים ששילמה הרשות הפלסטינית בזיקה לטרור מהכספים המועברים אליה מממשלת ישראל',
    'חוק יום הניצחון על גרמניה הנאצית',
    'חוק המרכז למורשת מלחמת ששת הימים, שחרור ירושלים ואיחודה, בגבעת התחמושת',
    'חוק קרן חינוך ארצות הברית-ישראל',
    'חוק מס הכנסה (ניכוי הוצאות הנפקה) (הוראת שעה)',
    'חוק פתיחת קבר של קטין יוצא תימן, המזרח או הבלקן לשם זיהוי ועריכת בדיקה גנטית לקשרי משפחה (הוראת שעה)',
    'חוק ליישום ההסכם בין ממשלת מדינת ישראל לבין ממשלת הרפובליקה היוונית בדבר המעמד של כוחותיהן',
    'חוק ליישום ההסכם בין ממשלת מדינת ישראל לבין ממשלת הרפובליקה של קפריסין בדבר המעמד של כוחותיהן',
    'חוק יום ציון לאומי לתרומתה ולפועלה של העדה הדרוזית',
    'חוק יום השחרור וההצלה מגרמניה הנאצית',
    'חוק למניעת הפצה ומימון של נשק להשמדה המונית',
    'חוק התקציב לשנת הכספים 2019',
    'חוק התכנית הכלכלית (תיקוני חקיקה ליישום המדיניות הכלכלית לשנת התקציב 2019)',
    'חוק איסור צריכת זנות (הוראת שעה ותיקון חקיקה)',
    'חוק התפזרות הכנסת העשרים',
    'חוק התפזרות הכנסת העשרים ואחת',
    'חוק הבחירות לכנסת העשרים ושתיים (הוראות מיוחדות לעניין ועדת הבחירות)',
    'חוק התפזרות הכנסת העשרים ושתיים והקדמת הבחירות',
    'חוק סמכויות מיוחדות להתמודדות עם נגיף הקורונה החדש (צווי סגירה מינהליים) (הוראת שעה)',
    'חוק הארכת תקופות וקיום דיונים בהיוועדות חזותית בענייני תכנון ובנייה (נגיף הקורונה החדש - הוראת שעה)',
    'חוק למתן שירותים חיוניים מרחוק (נגיף הקורונה החדש - הוראת שעה)',
    'חוק החזר מקדמה בשל ביטול אירוע (נגיף הקורונה החדש)',
    'חוק ההוצאה לפועל (הקפאת הגבלת רישיונות נהיגה) (נגיף הקורונה החדש - הוראת שעה)',
    'חוק לביטול העדכון של שכר חברי הכנסת בשנת 2021 (הוראת שעה)',
    'חוק לעניין ועדות הכנסת (תיקוני חקיקה והוראת שעה)',
    'חוק התקציב לשנת הכספים 2021',
    'חוק התקציב לשנת הכספים 2022',
    'חוק מענק סיוע לעסקים בשל ההשפעה הכלכלית של התפשטות זן אומיקרון של נגיף הקורונה החדש (הוראת שעה)',
    'חוק להסדרת אירוע הילולת רבי שמעון בר יוחאי בהר מירון (הוראת שעה)',
    'חוק ההתאמות הפיסקליות',
    'חוק ההתייעלות הכלכלית (תיקוני חקיקה להשגת יעדי התקציב לשנות התקציב 2023 ו-2024)',
    'חוק לעידוד תעשייה עתירת ידע (הוראת שעה)',
    'חוק אמנת הבנק האסייני לפיתוח',
    'חוק הארכת תקופות ודחיית מועדים (הוראת שעה – חרבות ברזל) (אישורים רגולטוריים, עיצומים כספיים ובדיקות מיתקני גז)',
    'חוק הגנה על מענקים מיוחדים (חרבות ברזל)',
    'חוק העברת מידע לצורך זיהוי או אימות זהות של אדם לרבות גופה, ואיתור נעדר או שבוי, הנדרשים בשל פעולות האיבה או פעולות המלחמה (הוראות שעה – חרבות ברזל)',
    'חוק הארכת תקופות (הוראת שעה – חרבות ברזל) (אומנה לילדים)',
    'חוק חינוך מיוחד (הוראת שעה – חרבות ברזל) (הארכת זכאות)',
    'חוק הענקת אזרחות כבוד לחללי מערכות ישראל',
    'חוק הארכת תקופות ודחיית מועדים (הוראת שעה – חרבות ברזל) (תכנון ובנייה ומקרקעי ציבור)',
    'חוק הארכת תקופות ודחיית מועדים (הוראת שעה – חרבות ברזל) (הליכי מס ומענקי סיוע)',
    'חוק תקציב נוסף לשנת הכספים 2023',
    'חוק הבוררות המסחרית הבין-לאומית',
    'חוק זכויות הדייר בדיור הציבורי (הוראת שעה – חרבות ברזל) (דייר ממשיך מיוחד)',
    'חוק לפיצוי קורבנות טרור (פיצויים לדוגמה)',
    'חוק תשלום מיוחד לשם השגת יעדי התקציב (הוראת שעה – חרבות ברזל)',
    'חוק יום משפחות היתומים בישראל',
    'חוק מגבלות על חזרתו של מורשע במעשה טרור לסביבת נפגעי העבירה',
    'חוק יום האחדות',
    'חוק הרשויות המקומיות (מימון בחירות) (הוראת שעה)',
    'חוק הרשות לחקירה בטיחותית בתעופה',
    'חוק יום לציון אירועי הפרהוד',
    'חוק הגנה על זכויות בדירת המשפחה של ילד שהורהו הומת בידי בן זוגו',
    'חוק מחיקת רישומים פליליים ומשטרתיים של יוצאי אתיופיה',
    'חוק הגישה לתוכן דיגיטלי לאחר פטירתו של אדם',
    'חוק יום בריאות הנפש',
    'חוק הקמת מאגר מידע גנטי של כלבים',
    'חוק נטילת אמצעי זיהוי ביומטריים מזרים, הפקת נתוני זיהוי ביומטריים ומאגר מידע',
    'חוק הספריות הציבוריות',
    'חוק הפרות תעבורה מינהליות',
    'חוק להפסקת פעילות אונר"א בשטח מדינת ישראל',
    'חוק להפסקת פעילות אונר"א',
    'חוק הבחירות לכנסת העשרים ושלוש (הוראות מיוחדות)',
    'חוק התפזרות הכנסת העשרים וארבע ומימון מפלגות',
    'חוק גירוש משפחות מחבלים',
    'חוק הבחירות לכנסת העשרים וחמש (הוראות מיוחדות ותיקוני חקיקה)',
    'חוק לתיקון דיני הבחירות לרשויות המקומיות (הוראת שעה)',
    'חוק מניעת מימון לייצוג משפטי בידי מדינת ישראל (חשוד, נאשם או מורשע בעבירת ביטחון - חרבות ברזל)',
    'חוק הגנה על הציבור מפני ארגוני פשיעה',
    'חוק ההתייעלות הכלכלית (תיקוני חקיקה להשגת יעדי התקציב לשנת התקציב 2025) (הקפאת שכר נושאי משרה ברשויות השלטון וברשויות מקומיות בשנת 2025)',
    'חוק הסדרת העיסוק בעבודה במערכת קירור או מיזוג אוויר',
    'חוק להנצחת זכרו של הרב חיים דרוקמן',
    'חוק איסור הכחשת אירועי טבח 7 באוקטובר 2023 (טבח שמיני עצרת)',
    'חוק להנצחת זכרו של מרן הרב עובדיה יוסף',
    'חוק יום לציון עליית יהודי תימן לישראל ולהנצחת זכרם של הנספים בדרך לישראל',
    'חוק להסדרה של הצבת כוורות, האבקה וייצור דבש',
    'חוק יום לציון מכתב 18 המשפחות היהודיות מגאורגיה',
    'חוק להסדרת מגורים בשטחי מרעה',
    'חוק התחשבנות בין בתי חולים לקופות חולים (בריאות הנפש)',
    'חוק להשגת יעדי התקציב וליישום המדיניות הכלכלית לשנת התקציב 2025 (תיקוני חקיקה)',
    'חוק שיקום נרחב לחבל התקומה כאזור מיקוד לאומי וסיוע ליישובים הסמוכים אליו',
    'חוק קיום דיונים בהיוועדות חזותית בהשתתפות עצורים, אסירים וכלואים (הוראת שעה – חרבות ברזל)',
    'חוק הרשות הלאומית למאבק בעוני'
]
unique_law_names_no_dates = sorted(list(set(law_names_no_dates_input)))

def sanitize_filename(name):
    name = re.sub(r'[\\/*?:"<>|]', "_", name)
    name = re.sub(r'\s+', '_', name)
    name = re.sub(r'_+', '_', name)
    return name[:150]

def get_resolved_page_title_after_http_redirects(page_name_with_underscores_for_lookup, session):
    """
    Resolves HTTP redirects for a given page name.
    Returns the final page title (with spaces) after HTTP redirects, or None on error.
    """
    wiki_url_to_lookup = WIKI_PAGE_URL_FORMAT.format(page_name_with_underscores_for_lookup)
    print(f"  Resolving HTTP redirects. Initial lookup URL: {wiki_url_to_lookup}")
    try:
        final_url_str = None
        try:
            # Try HEAD first for efficiency
            head_response = session.head(wiki_url_to_lookup, timeout=15, allow_redirects=True)
            head_response.raise_for_status()
            final_url_str = head_response.url
        except requests.exceptions.RequestException as e_head:
            print(f"    HEAD request for {wiki_url_to_lookup} failed ({e_head}), trying GET.")
            try:
                get_response = session.get(wiki_url_to_lookup, timeout=30, allow_redirects=True)
                get_response.raise_for_status()
                final_url_str = get_response.url
            except requests.exceptions.RequestException as e_get:
                print(f"    GET request also failed for {wiki_url_to_lookup}: {e_get}")
                return None
        
        if not final_url_str: return None # Should be caught by exceptions above

        print(f"    Final URL after HTTP redirects: {final_url_str}")
        parsed_final_url = urllib.parse.urlparse(final_url_str)
        actual_title = None

        if parsed_final_url.path.startswith("/wiki/"):
            title_from_path = parsed_final_url.path[len("/wiki/"):]
            actual_title = urllib.parse.unquote(title_from_path).replace("_", " ")
        elif parsed_final_url.path.startswith("/w/index.php"):
            query_params = urllib.parse.parse_qs(parsed_final_url.query)
            if 'title' in query_params:
                actual_title = query_params['title'][0]
        
        if actual_title:
            print(f"    Title after HTTP redirects: '{actual_title}'")
            return actual_title
        else:
            # Fallback: if structure was unexpected, assume original lookup name (spaces restored) was it.
            original_title_with_spaces = page_name_with_underscores_for_lookup.replace("_", " ")
            print(f"    Could not extract title from final URL. Assuming initial was canonical for HTTP: '{original_title_with_spaces}'")
            return original_title_with_spaces

    except Exception as e: # Catch any other unexpected error during resolution
        print(f"    Unexpected error resolving HTTP redirects for '{page_name_with_underscores_for_lookup}': {e}")
        return None

def get_wikitext(url, session):
    try:
        response = session.get(url, timeout=30)
        response.raise_for_status()
        response.encoding = response.apparent_encoding if response.apparent_encoding else 'utf-8'
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"    Error fetching wikitext from {url}: {e}")
        return None

def get_history_oldids(page_title_for_history, session):
    """
    Fetches the history page for 'page_title_for_history', extracts all oldids,
    and returns a sorted list of oldid strings (oldest first). Returns empty list on failure.
    """
    encoded_title = urllib.parse.quote(page_title_for_history)
    history_page_url = INDEX_PHP_URL_FORMAT_HISTORY.format(encoded_title)
    print(f"    Fetching history for page '{page_title_for_history}' from: {history_page_url}")
    try:
        response = session.get(history_page_url, timeout=30)
        response.raise_for_status()
        response.encoding = response.apparent_encoding if response.apparent_encoding else 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')

        history_container = soup.find('ul', {'id': 'pagehistory'})
        if not history_container: history_container = soup.find('section', {'id': 'pagehistory'})
        if not history_container:
            mw_content = soup.find('div', {'id': 'mw-content-text'})
            if mw_content:
                history_form = mw_content.find('form', {'id': 'mw-history-compare'})
                if history_form:
                    history_container = history_form.find('section', class_='mw-pager-body')
                    if not history_container: history_container = history_form.find('ul')
                if not history_container: history_container = mw_content.find('ul') 
        
        if not history_container:
            print(f"    Could not find a suitable history list container for '{page_title_for_history}'.")
            return []
        
        all_oldids_on_page = set()
        revision_lis = history_container.find_all('li', attrs={'data-mw-revid': True})
        for rev_li in revision_lis:
            revid = rev_li.get('data-mw-revid')
            if revid and revid.isdigit(): all_oldids_on_page.add(int(revid))
            else:
                radio_input = rev_li.find('input', {'name': 'oldid', 'type': 'radio'})
                if radio_input and radio_input.get('value', '').isdigit():
                    all_oldids_on_page.add(int(radio_input['value']))
        
        radio_inputs = soup.find_all('input', {'name': 'oldid', 'type': 'radio'})
        for radio in radio_inputs:
            if radio.get('value', '').isdigit(): all_oldids_on_page.add(int(radio['value']))
        
        if not all_oldids_on_page:
            print(f"    No oldids extracted from history page for '{page_title_for_history}'.")
            return []
        
        sorted_oldids_str = [str(oid) for oid in sorted(list(all_oldids_on_page))]
        print(f"    Collected {len(sorted_oldids_str)} unique oldids for '{page_title_for_history}'. Oldest: {sorted_oldids_str[0] if sorted_oldids_str else 'N/A'}")
        return sorted_oldids_str

    except requests.exceptions.RequestException as e:
        print(f"    Error fetching history page for '{page_title_for_history}': {e}")
        return []
    except Exception as e:
        print(f"    Unexpected error parsing history for '{page_title_for_history}': {e}")
        return []

def download_law_versions(law_title_from_input_list, session):
    print(f"Processing: {law_title_from_input_list}")
    
    # --- Stage 1: Resolve HTTP redirects, then follow wikitext redirects for current content ---
    page_name_for_http_lookup = law_title_from_input_list.replace(" ", "_")
    
    # title_after_http_redirects is the page name MediaWiki considers canonical after *only* HTTP redirects
    title_after_http_redirects = get_resolved_page_title_after_http_redirects(page_name_for_http_lookup, session)
    
    if not title_after_http_redirects:
        print(f"  Skipping '{law_title_from_input_list}' due to failure in resolving initial page title via HTTP.")
        return

    # title_for_current_content_and_history will be updated if wikitext redirects are found in content
    title_for_current_content_and_history = title_after_http_redirects 
    
    current_wikitext = None

    for hop in range(MAX_WIKITEXT_REDIRECT_HOPS_FOR_CURRENT + 1): # +1 to allow one last fetch for redirect content if max hops hit
        encoded_title_for_fetch = urllib.parse.quote(title_for_current_content_and_history)
        raw_url_to_fetch = INDEX_PHP_URL_FORMAT_RAW_BY_TITLE.format(encoded_title_for_fetch)
        
        print(f"  Fetching current content (hop {hop+1}) for page '{title_for_current_content_and_history}': {raw_url_to_fetch}")
        
        wikitext_at_hop = get_wikitext(raw_url_to_fetch, session)
        
        if not wikitext_at_hop:
            print(f"    Failed to download wikitext for '{title_for_current_content_and_history}' at hop {hop+1}.")
            if hop == 0 : # If first fetch (for title_after_http_redirects) fails
                 print(f"    Initial content fetch for '{title_for_current_content_and_history}' failed. Cannot get current or original.")
                 return 
            # If a redirect target fetch fails, current_wikitext remains from previous successful fetch (or None)
            # The loop will break, and current_wikitext will be the last successfully fetched one.
            break 

        current_wikitext = wikitext_at_hop # Store this hop's wikitext

        # Check if this fetched wikitext is a redirect
        # Regex to capture target: #REDIRECT [[Target Page]] or #הפניה [[Target Page]]
        redirect_match = re.match(r"^\s*#(?:REDIRECT|הפניה)\s*\[\[\s*([^\]]+)\s*\]\]", current_wikitext, re.IGNORECASE)
        
        if redirect_match:
            if hop >= MAX_WIKITEXT_REDIRECT_HOPS_FOR_CURRENT:
                print(f"    Max wikitext redirect hops ({MAX_WIKITEXT_REDIRECT_HOPS_FOR_CURRENT}) reached. Using content of last redirect page itself: '{title_for_current_content_and_history}'.")
                # current_wikitext is already set to the content of this redirect page
                break 

            redirect_target_title_text = redirect_match.group(1).strip()
            # Normalize potential namespace prefixes (e.g., "ויקיטקסט:שם הדף" -> "שם הדף")
            if ":" in redirect_target_title_text:
                redirect_target_title_text = redirect_target_title_text.split(":", 1)[-1].strip()

            print(f"    Content of '{title_for_current_content_and_history}' is a wikitext redirect to: '{redirect_target_title_text}'. Following.")
            title_for_current_content_and_history = redirect_target_title_text # Update for next hop
        else:
            # Not a wikitext redirect, this is the content we want for "current"
            print(f"    Content of '{title_for_current_content_and_history}' is not a wikitext redirect.")
            break # Found non-wikitext-redirect content
    # --- End of Stage 1: Current Content Fetching ---

    if current_wikitext:
        # Use original input name for the base filename to maintain user's reference
        base_filename = sanitize_filename(law_title_from_input_list)
        filepath_current = os.path.join(OUTPUT_DIR, f"{base_filename}_current.txt")
        os.makedirs(os.path.dirname(filepath_current), exist_ok=True)
        with open(filepath_current, "w", encoding="utf-8") as f:
            f.write(current_wikitext)
        print(f"    Saved current version (content from page '{title_for_current_content_and_history}') to {filepath_current}")
    else:
        print(f"    Failed to obtain final current wikitext for '{law_title_from_input_list}'. Skipping original.")
        return

    time.sleep(REQUEST_DELAY_SECONDS)

    # --- Stage 2: Download "original" version from the history of title_for_current_content_and_history ---
    # This title is the one whose actual content was fetched for "current" (after all redirects).
    
    sorted_oldids = get_history_oldids(title_for_current_content_and_history, session)

    if not sorted_oldids:
        print(f"    Could not retrieve any oldids for page '{title_for_current_content_and_history}'. Skipping original version.")
        return

    chosen_original_oldid = None
    chosen_original_wikitext = None
    
    # Iterate through the OLDEST oldids of 'title_for_current_content_and_history'
    for i, test_oldid in enumerate(sorted_oldids):
        if i >= MAX_ORIGINAL_VERSION_ATTEMPTS and chosen_original_wikitext is not None: # Stop if max attempts AND we have a fallback
            print(f"    Reached max attempts ({MAX_ORIGINAL_VERSION_ATTEMPTS}) for finding non-stub/redirect original for '{title_for_current_content_and_history}'. Using best found so far (oldid {chosen_original_oldid}).")
            break
        if i >= MAX_ORIGINAL_VERSION_ATTEMPTS and chosen_original_wikitext is None: # Stop if max attempts and NO fallback yet
            print(f"    Reached max attempts ({MAX_ORIGINAL_VERSION_ATTEMPTS}) and no version content fetched. Cannot select original.")
            break


        print(f"    Attempt {i+1} for original of '{title_for_current_content_and_history}': testing oldid {test_oldid}")
        
        encoded_title_for_oldid_fetch = urllib.parse.quote(title_for_current_content_and_history)
        oldid_raw_url = INDEX_PHP_URL_FORMAT_OLDID_RAW.format(encoded_title_for_oldid_fetch, test_oldid)
        wikitext_of_oldid = get_wikitext(oldid_raw_url, session)

        if not wikitext_of_oldid:
            print(f"      Failed to fetch content for oldid {test_oldid} of '{title_for_current_content_and_history}'. Skipping this attempt.")
            if chosen_original_wikitext is None and i == 0 : # If it's the very first oldid and it failed to fetch
                chosen_original_oldid = test_oldid # Store its ID for a potential "failed to download" message
            continue 

        # Store the first successfully fetched oldid's content as a definite fallback
        if chosen_original_wikitext is None: 
            chosen_original_oldid = test_oldid
            chosen_original_wikitext = wikitext_of_oldid
            print(f"      Setting oldid {test_oldid} of '{title_for_current_content_and_history}' as initial/fallback original.")

        is_redirect = wikitext_of_oldid.strip().lower().startswith(("#redirect", "#הפניה"))
        
        # Stub heuristic: for the content of the OLDID of 'title_for_current_content_and_history'
        base_name_for_stub_check = title_for_current_content_and_history.split('(')[0].strip()
        # More robust stub check: consider very short content, or content that is mostly just templating around the title
        is_stub = False
        if not is_redirect:
            cleaned_text = wikitext_of_oldid.strip()
            # Heuristic 1: very short
            if len(cleaned_text) < (len(base_name_for_stub_check) + 75): # Reduced buffer slightly
                is_stub = True
            # Heuristic 2: contains title and very few lines (e.g. <= 5 lines after {{ח:התחלה}}, {{ח:כותרת}}, {{ח:סוף}})
            elif base_name_for_stub_check.lower() in cleaned_text.lower() and cleaned_text.count('\n') < 7:
                is_stub = True
                
        if not is_redirect and not is_stub:
            print(f"      Oldid {test_oldid} of '{title_for_current_content_and_history}' is NOT a redirect and NOT a stub. Selecting this as original.")
            chosen_original_oldid = test_oldid
            chosen_original_wikitext = wikitext_of_oldid
            break # Found a good version, exit loop
        else:
            # This oldid is a redirect or stub. If it was the first one, it's already our fallback.
            # If it's a subsequent one, we don't update the fallback unless it's better (which it isn't if it's also bad).
            if is_redirect:
                print(f"      Oldid {test_oldid} of '{title_for_current_content_and_history}' is a redirect. Content: {wikitext_of_oldid.strip()[:120]}...")
            if is_stub: # This implies not is_redirect due to `is_stub` definition
                print(f"      Oldid {test_oldid} of '{title_for_current_content_and_history}' is likely a stub. Content: {wikitext_of_oldid.strip()[:120]}...")
            if i < MAX_ORIGINAL_VERSION_ATTEMPTS - 1 and i < len(sorted_oldids) -1 : # Check if there are more attempts/oldids
                 print(f"      Trying next older version of '{title_for_current_content_and_history}'...")
    # --- End of loop for finding original ---

    if chosen_original_wikitext:
        base_filename_for_original = sanitize_filename(law_title_from_input_list) # Filename based on original query
        filepath_original = os.path.join(OUTPUT_DIR, f"{base_filename_for_original}_original_oldid_{chosen_original_oldid}.txt")
        os.makedirs(os.path.dirname(filepath_original), exist_ok=True)
        with open(filepath_original, "w", encoding="utf-8") as f:
            f.write(chosen_original_wikitext)
        print(f"    Saved original version (oldid {chosen_original_oldid} of page '{title_for_current_content_and_history}') to {filepath_original}")

        # Check characteristics of the *saved* chosen_original_wikitext for the warning message
        is_redirect_final = chosen_original_wikitext.strip().lower().startswith(("#redirect", "#הפניה"))
        base_name_for_stub_check_final = title_for_current_content_and_history.split('(')[0].strip()
        is_stub_final = False
        if not is_redirect_final:
            cleaned_text_final = chosen_original_wikitext.strip()
            if len(cleaned_text_final) < (len(base_name_for_stub_check_final) + 75): is_stub_final = True
            elif base_name_for_stub_check_final.lower() in cleaned_text_final.lower() and cleaned_text_final.count('\n') < 7: is_stub_final = True
        
        if is_redirect_final:
            print(f"    >>>> WARNING: The saved original version (oldid {chosen_original_oldid} of '{title_for_current_content_and_history}') IS A REDIRECT.")
        elif is_stub_final:
            print(f"    >>>> WARNING: The saved original version (oldid {chosen_original_oldid} of '{title_for_current_content_and_history}') IS LIKELY A STUB.")
    
    elif chosen_original_oldid: # No wikitext, but we have an ID (implies fetch failed for the designated fallback)
         print(f"    Failed to download content for the chosen original oldid {chosen_original_oldid} of page '{title_for_current_content_and_history}'.")
    elif sorted_oldids: # We had oldids, but couldn't fetch content for ANY initial oldids.
         print(f"    Failed to download content for any of the initial oldids of '{title_for_current_content_and_history}' (e.g., {sorted_oldids[0]}). No original saved.")
    else: # No oldids were found in the first place for title_for_current_content_and_history.
        print(f"    Could not determine or download any original version for page '{title_for_current_content_and_history}'.")


def main():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"Created directory: {OUTPUT_DIR}")

    session = requests.Session()
    session.headers.update({
        "User-Agent": "LawWikitextDownloader/1.7 (Python script; contact: your@email.com or project/repo URL)"
    })
    
    print(f"Processing {len(unique_law_names_no_dates)} unique law titles.")
    processed_count = 0
    for law_title_item in unique_law_names_no_dates:
        processed_count += 1
        print(f"\n--- Item {processed_count}/{len(unique_law_names_no_dates)} ---")
        download_law_versions(law_title_item, session)
        time.sleep(REQUEST_DELAY_SECONDS)

    print("\nProcessing complete.")

if __name__ == "__main__":
    main()