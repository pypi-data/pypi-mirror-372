import requests
from bs4 import BeautifulSoup
import urllib.parse
import os
import time
import re

# --- Configuration ---
BASE_URL = "https://he.wikisource.org"
WIKI_PAGE_URL_FORMAT = BASE_URL + "/wiki/{}"
# Using &dir=prev&limit=500 to get as many old revisions as possible on one page,
# increasing the chance the true oldest is present.
# The limit might be capped by the server (often at 500 or 5000).
INDEX_PHP_URL_FORMAT_HISTORY = BASE_URL + "/w/index.php?title={}&action=history&dir=prev&limit=500"
INDEX_PHP_URL_FORMAT_RAW = BASE_URL + "/w/index.php?title={}"
OUTPUT_DIR = "Data/wikitext_laws"
REQUEST_DELAY_SECONDS = 2

# --- List of Laws ---
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
    'חוק הרשות הלאומית למאבק בעוני'
]
# Remove the Hebrew date suffixes from the law names
unique_law_names_no_dates = sorted(list(set(law_names_no_dates_input)))


def sanitize_filename(name):
    name = re.sub(r'[\\/*?:"<>|]', "_", name)
    name = re.sub(r'_+', '_', name)
    return name[:150]

def get_wikitext(url, session):
    try:
        response = session.get(url, timeout=30) # Increased timeout slightly
        response.raise_for_status()
        response.encoding = response.apparent_encoding if response.apparent_encoding else 'utf-8'
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"    Error fetching {url}: {e}")
        return None

def get_original_oldid(history_page_url, session):
    """
    Fetches the history page (using &dir=prev&limit=500 to get older revisions first),
    extracts all oldids from list items (data-mw-revid or input[name=oldid]),
    and returns the numerically smallest one found on that page.
    """
    try:
        print(f"    Fetching history from: {history_page_url}")
        response = session.get(history_page_url, timeout=30)
        response.raise_for_status()
        response.encoding = response.apparent_encoding if response.apparent_encoding else 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find the main container for history entries
        # It could be <ul id="pagehistory"> or <section id="pagehistory">
        # or even just <li> tags directly under #mw-content-text > form > section or #mw-content-text > ul
        history_container = soup.find('ul', {'id': 'pagehistory'})
        if not history_container:
            history_container = soup.find('section', {'id': 'pagehistory'})
        
        if not history_container:
            # More general search if specific IDs are not found
            mw_content = soup.find('div', {'id': 'mw-content-text'})
            if mw_content:
                # Look for forms that might contain the history list (common pattern)
                history_form = mw_content.find('form', {'id': 'mw-history-compare'})
                if history_form:
                    history_container = history_form.find('section', class_='mw-pager-body') # As per your HTML
                    if not history_container:
                         history_container = history_form.find('ul') # More generic ul within the form
                if not history_container: # If not in a form, try a direct ul
                    history_container = mw_content.find('ul') 
            if history_container:
                 print(f"    Found history container using fallback selector.")
            else:
                print(f"    Could not find a suitable history list container (ul/section#pagehistory or fallback) on {history_page_url}")
                # print(f"    Page content sample: {soup.prettify()[:2000]}") # For debugging
                return None
        
        all_oldids_on_page = []

        # Method 1: Look for <li> elements with 'data-mw-revid'
        # These are often the direct list items for revisions.
        revision_lis = history_container.find_all('li', attrs={'data-mw-revid': True})
        if revision_lis:
            print(f"    Found {len(revision_lis)} list items with data-mw-revid.")
            for rev_li in revision_lis:
                revid = rev_li.get('data-mw-revid')
                if revid and revid.isdigit():
                    all_oldids_on_page.append(int(revid))
                else:
                    # Try to get from radio button inside this li as a backup for this specific li
                    radio_input = rev_li.find('input', {'name': 'oldid', 'type': 'radio'})
                    if radio_input and radio_input.get('value', '').isdigit():
                        all_oldids_on_page.append(int(radio_input['value']))


        # Method 2 (Fallback or supplementary): Look for all radio inputs named 'oldid'
        # This is useful if data-mw-revid is not consistently present or if the structure is different.
        # We do this to catch any missed oldids if Method 1 wasn't exhaustive for the page structure.
        # Use a set to avoid duplicates if both methods pick up the same IDs.
        oldid_values_from_inputs = set()
        radio_inputs = soup.find_all('input', {'name': 'oldid', 'type': 'radio'}) # Search whole soup for these inputs
        if radio_inputs:
             print(f"    Found {len(radio_inputs)} radio inputs with name='oldid'.")
             for radio in radio_inputs:
                 if radio.get('value', '').isdigit():
                     oldid_values_from_inputs.add(int(radio['value']))
        
        all_oldids_on_page.extend(list(oldid_values_from_inputs)) # Add any unique ones found
        
        # Remove duplicates that might have been added by both methods
        if all_oldids_on_page:
            all_oldids_on_page = sorted(list(set(all_oldids_on_page)))

        if not all_oldids_on_page:
            print(f"    No oldids could be extracted from the history page {history_page_url}")
            # For debugging, save the problematic HTML
            # with open(f"debug_history_page_{sanitize_filename(history_page_url)}.html", "w", encoding="utf-8") as f_debug:
            #     f_debug.write(soup.prettify())
            # print(f"    Saved debug HTML for {history_page_url}")
            return None
        
        numerically_lowest_oldid = min(all_oldids_on_page)
        print(f"    Collected {len(all_oldids_on_page)} unique oldids. Smallest found: {numerically_lowest_oldid}")
        return str(numerically_lowest_oldid)

    except requests.exceptions.RequestException as e:
        print(f"    Error fetching history page {history_page_url}: {e}")
        return None
    except Exception as e:
        print(f"    An unexpected error occurred while parsing history page {history_page_url}: {e}")
        # import traceback
        # traceback.print_exc() # For more detailed error logging
        return None

def download_law_versions(law_title_no_date, session):
    print(f"Processing: {law_title_no_date}")
    url_title_component = law_title_no_date.replace(" ", "_")
    encoded_title = urllib.parse.quote(url_title_component)
    base_filename = sanitize_filename(law_title_no_date)

    # 1. Download current version
    current_raw_url = WIKI_PAGE_URL_FORMAT.format(encoded_title) + "?action=raw"
    print(f"  Fetching current version: {current_raw_url}")
    current_wikitext = get_wikitext(current_raw_url, session)
    if current_wikitext:
        filepath = os.path.join(OUTPUT_DIR, f"{base_filename}_current.txt")
        os.makedirs(os.path.dirname(filepath), exist_ok=True) # Ensure directory exists
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(current_wikitext)
        print(f"    Saved current version to {filepath}")
    else:
        print(f"    Failed to download current version for {law_title_no_date}. Skipping original.")
        return 

    time.sleep(REQUEST_DELAY_SECONDS)

    # 2. Download original version
    history_page_url_for_oldid = INDEX_PHP_URL_FORMAT_HISTORY.format(encoded_title)
    original_oldid = get_original_oldid(history_page_url_for_oldid, session)

    if original_oldid:
        print(f"    Determined original (numerically lowest from page) oldid: {original_oldid}")
        original_raw_url = INDEX_PHP_URL_FORMAT_RAW.format(encoded_title) + f"&oldid={original_oldid}&action=raw"
        print(f"  Fetching original version ({original_oldid}): {original_raw_url}")
        original_wikitext = get_wikitext(original_raw_url, session)
        if original_wikitext:
            filepath = os.path.join(OUTPUT_DIR, f"{base_filename}_original_oldid_{original_oldid}.txt")
            os.makedirs(os.path.dirname(filepath), exist_ok=True) # Ensure directory exists
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(original_wikitext)
            print(f"    Saved original version to {filepath}")
        else:
            print(f"    Failed to download original version for oldid {original_oldid}")
    else:
        print(f"    Could not determine original oldid for {law_title_no_date}.")

def main():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"Created directory: {OUTPUT_DIR}")

    session = requests.Session()
    session.headers.update({
        "User-Agent": "LawWikitextDownloader/1.4 (Python script; contact: your@email.com or project/repo URL)"
    })
    
    print(f"Processing {len(unique_law_names_no_dates)} unique law titles (dates removed).")

    for law_title_no_date_item in unique_law_names_no_dates:
        download_law_versions(law_title_no_date_item, session)
        print("-" * 30)
        time.sleep(REQUEST_DELAY_SECONDS)

    print("Processing complete.")

if __name__ == "__main__":
    main()