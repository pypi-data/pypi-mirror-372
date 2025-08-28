import json
import re
from functools import lru_cache

import dateparser
from pyquery import PyQuery as pq

CATEGORY_CODES_BY_COUNTRY = [
    {
        "country": "us",
        "categoryCodes": {
            "all departments": "aps",
            "audible books & originals": "audible",
            "alexa skills": "alexa-skills",
            "amazon devices": "amazon-devices",
            "amazon fresh": "amazonfresh",
            "amazon warehouse": "warehouse-deals",
            "appliances": "appliances",
            "apps & games": "mobile-apps",
            "arts, crafts & sewing": "arts-crafts",
            "automotive parts & accessories": "automotive",
            "baby": "fashion-baby",
            "beauty & personal care": "beauty",
            "books": "stripbooks",
            "cds & vinyl": "popular",
            "cell phones & accessories": "mobile",
            "clothing, shoes & jewelry": "fashion",
            "women": "fashion-womens",
            "men": "fashion-mens",
            "girls": "fashion-girls",
            "boys": "fashion-boys",
            "collectibles & fine art": "collectibles",
            "computers": "computers",
            "courses": "courses",
            "credit and payment cards": "financial",
            "digital music": "digital-music",
            "electronics": "electronics",
            "garden & outdoor": "lawngarden",
            "gift cards": "gift-cards",
            "grocery & gourmet food": "grocery",
            "handmade": "handmade",
            "health, household & baby care": "hpc",
            "home & business services": "local-services",
            "home & kitchen": "garden",
            "industrial & scientific": "industrial",
            "just for prime": "prime-exclusive",
            "kindle store": "digital-text",
            "luggage & travel gear": "fashion-luggage",
            "luxury beauty": "luxury-beauty",
            "magazine subscriptions": "magazines",
            "movies & tv": "movies-tv",
            "musical instruments": "mi",
            "office products": "office-products",
            "pet supplies": "pets",
            "prime pantry": "pantry",
            "prime video": "instant-video",
            "software": "software",
            "sports & outdoors": "sporting",
            "tools & home improvement": "tools",
            "toys & games": "toys-and-games",
            "vehicles": "vehicles",
            "video games": "videogames"
        }
    },
    {
        "country": "us-intl",
        "categoryCodes": {
            "all departments": "aps",
            "arts & crafts": "arts-crafts",
            "automotive": "automotive",
            "baby": "baby-products",
            "beauty & personal care": "beauty",
            "books": "stripbooks",
            "computers": "computers",
            "digital music": "digital-music",
            "electronics": "electronics",
            "kindle store": "digital-text",
            "prime video": "instant-video",
            "women's fashion": "fashion-womens",
            "men's fashion": "fashion-mens",
            "girls' fashion": "fashion-girls",
            "boys' fashion": "fashion-boys",
            "deals": "deals",
            "health & household": "hpc",
            "home & kitchen": "kitchen",
            "industrial & scientific": "industrial",
            "luggage": "luggage",
            "movies & tv": "movies-tv",
            "music, cds & vinyl": "music",
            "pet supplies": "pets",
            "software": "software",
            "sports & outdoors": "sporting",
            "tools & home improvement": "tools",
            "toys & games": "toys-and-games",
            "video games": "videogames"
        }
    },
    {
        "country": "ca",
        "categoryCodes": {
            "all departments": "aps",
            "alexa skills": "alexa-skills",
            "amazon devices": "amazon-devices",
            "amazon warehouse deals": "warehouse-deals",
            "apps & games": "mobile-apps",
            "automotive": "automotive",
            "baby": "baby",
            "beauty": "beauty",
            "books": "stripbooks",
            "clothing & accessories": "apparel",
            "electronics": "electronics",
            "gift cards": "gift-cards",
            "grocery": "grocery",
            "handmade": "handmade",
            "health & personal care": "hpc",
            "home & kitchen": "kitchen",
            "industrial & scientific": "industrial",
            "jewelry": "jewelry",
            "kindle store": "digital-text",
            "livres en français": "french-books",
            "luggage & bags": "luggage",
            "luxury beauty": "luxury-beauty",
            "movies & tv": "dvd",
            "music": "popular",
            "musical instruments, stage & studio": "mi",
            "office products": "office-products",
            "patio, lawn & garden": "lawngarden",
            "pet supplies": "pets",
            "shoes & handbags": "shoes",
            "software": "software",
            "sports & outdoors": "sporting",
            "tools & home improvement": "tools",
            "toys & games": "toys",
            "video games": "videogames",
            "watches": "watches"
        }
    },
    {
        "country": "uk",
        "categoryCodes": {
            "all departments": "aps",
            "alexa skills": "alexa-skills",
            "amazon devices": "amazon-devices",
            "amazon fresh": "amazonfresh",
            "amazon global store": "amazon-global-store",
            "amazon pantry": "pantry",
            "amazon warehouse": "warehouse-deals",
            "apps & games": "mobile-apps",
            "baby": "baby",
            "beauty": "beauty",
            "books": "stripbooks",
            "car & motorbike": "automotive",
            "cds & vinyl": "popular",
            "classical music": "classical",
            "clothing": "clothing",
            "computers & accessories": "computers",
            "digital music ": "digital-music",
            "diy & tools": "diy",
            "dvd & blu-ray": "dvd",
            "electronics & photo": "electronics",
            "fashion": "fashion",
            "garden & outdoors": "outdoor",
            "gift cards": "gift-cards",
            "grocery": "grocery",
            "handmade": "handmade",
            "health & personal care": "drugstore",
            "home & business services": "local-services",
            "home & kitchen": "kitchen",
            "industrial & scientific": "industrial",
            "jewellery": "jewelry",
            "kindle store": "digital-text",
            "large appliances": "appliances",
            "lighting": "lighting",
            "luggage": "luggage",
            "luxury beauty": "luxury-beauty",
            "musical instruments & dj": "mi",
            "pc & video games": "videogames",
            "pet supplies": "pets",
            "prime video": "instant-video",
            "shoes & bags": "shoes",
            "software": "software",
            "sports & outdoors": "sports",
            "stationery & office supplies": "office-products",
            "toys & games": "toys",
            "vhs": "vhs",
            "watches": "watches"
        }
    },
    {
        "country": "fr",
        "categoryCodes": {
            "toutes nos catégories": "aps",
            "alexa skills": "alexa-skills",
            "amazon offres reconditionnées": "warehouse-deals",
            "amazon pantry": "pantry",
            "animalerie": "pets",
            "appareils amazon": "amazon-devices",
            "applis & jeux": "mobile-apps",
            "auto et moto": "automotive",
            "bagages": "luggage",
            "beauté et parfum": "beauty",
            "beauté prestige": "luxury-beauty",
            "bijoux": "jewelry",
            "boutique chèques-cadeaux": "gift-cards",
            "boutique kindle": "digital-text",
            "bricolage": "diy",
            "bébés & puériculture": "baby",
            "chaussures et sacs": "shoes",
            "cuisine & maison": "kitchen",
            "dvd & blu-ray": "dvd",
            "epicerie": "grocery",
            "fournitures de bureau": "office-products",
            "gros électroménager": "appliances",
            "handmade": "handmade",
            "high-tech": "electronics",
            "hygiène et santé": "hpc",
            "informatique": "computers",
            "instruments de musique & sono": "mi",
            "jardin": "garden",
            "jeux et jouets": "toys",
            "jeux vidéo": "videogames",
            "livres anglais et étrangers": "english-books",
            "livres en français": "stripbooks",
            "logiciels": "software",
            "luminaires et eclairage": "lighting",
            "mode": "fashion",
            "montres": "watches",
            "musique : cd & vinyles": "popular",
            "musique classique": "classical",
            "secteur industriel & scientifique": "industrial",
            "sports et loisirs": "sports",
            "téléchargement de musique": "digital-music",
            "vêtements et accessoires": "clothing"
        }
    },
    {
        "country": "de",
        "categoryCodes": {
            "alle kategorien": "aps",
            "alexa skills": "alexa-skills",
            "amazon fresh": "amazonfresh",
            "amazon geräte": "amazon-devices",
            "amazon global store": "amazon-global-store",
            "amazon pantry": "pantry",
            "amazon warehouse": "warehouse-deals",
            "apps & spiele": "mobile-apps",
            "audible hörbücher": "audible",
            "auto & motorrad": "automotive",
            "baby": "baby",
            "baumarkt": "diy",
            "beauty": "beauty",
            "bekleidung": "clothing",
            "beleuchtung": "lighting",
            "bücher": "stripbooks",
            "bücher (fremdsprachig)": "english-books",
            "bürobedarf & schreibwaren": "office-products",
            "computer & zubehör": "computers",
            "drogerie & körperpflege": "drugstore",
            "dvd & blu-ray": "dvd",
            "elektro-großgeräte": "appliances",
            "elektronik & foto": "electronics",
            "fashion": "fashion",
            "games": "videogames",
            "garten": "outdoor",
            "geschenkgutscheine": "gift-cards",
            "gewerbe, industrie & wissenschaft": "industrial",
            "handmade": "handmade",
            "haustier": "pets",
            "kamera & foto": "photo",
            "kindle-shop": "digital-text",
            "klassik": "classical",
            "koffer, rucksäcke & taschen ": "luggage",
            "küche, haushalt & wohnen": "kitchen",
            "lebensmittel & getränke": "grocery",
            "luxury beauty": "luxury-beauty",
            "musik-cds & vinyl": "popular",
            "musik-downloads": "digital-music",
            "musikinstrumente & dj-equipment": "mi",
            "prime video": "instant-video",
            "schmuck": "jewelry",
            "schuhe & handtaschen": "shoes",
            "software": "software",
            "spielzeug": "toys",
            "sport & freizeit": "sports",
            "uhren": "watches",
            "zeitschriften": "magazines"
        }
    },
    {
        "country": "es",
        "categoryCodes": {
            "todos los departamentos": "aps",
            "alexa skills": "alexa-skills",
            "alimentación y bebidas": "grocery",
            "amazon pantry": "pantry",
            "appstore para android": "mobile-apps",
            "bebé": "baby",
            "belleza": "beauty",
            "bricolaje y herramientas": "diy",
            "cheques regalo": "gift-cards",
            "coche - renting": "vehicles",
            "coche y moto - piezas y accesorios": "automotive",
            "deportes y aire libre": "sporting",
            "dispositivos de amazon": "amazon-devices",
            "electrónica": "electronics",
            "equipaje": "luggage",
            "grandes electrodomésticos": "appliances",
            "handmade": "handmade",
            "hogar y cocina": "kitchen",
            "iluminación": "lighting",
            "industria y ciencia": "industrial",
            "informática": "computers",
            "instrumentos musicales": "mi",
            "jardín": "lawngarden",
            "joyería": "jewelry",
            "juguetes y juegos": "toys",
            "libros": "stripbooks",
            "moda": "fashion",
            "música digital": "digital-music",
            "música: cds y vinilos": "popular",
            "oficina y papelería": "office-products",
            "películas y tv": "dvd",
            "productos para mascotas": "pets",
            "productos reacondicionados": "warehouse-deals",
            "relojes": "watches",
            "ropa y accesorios": "apparel",
            "salud y cuidado personal": "hpc",
            "software": "software",
            "tienda kindle": "digital-text",
            "videojuegos": "videogames",
            "zapatos y complementos": "shoes"
        }
    },
    {
        "country": "it",
        "categoryCodes": {
            "tutte le categorie": "aps",
            "abbigliamento": "apparel",
            "alexa skill": "alexa-skills",
            "alimentari e cura della casa": "grocery",
            "amazon pantry": "pantry",
            "amazon warehouse": "warehouse-deals",
            "app e giochi": "mobile-apps",
            "auto e moto": "automotive",
            "bellezza": "beauty",
            "buoni regalo": "gift-cards",
            "cancelleria e prodotti per ufficio": "office-products",
            "casa e cucina": "kitchen",
            "cd e vinili ": "popular",
            "dispositivi amazon": "amazon-devices",
            "elettronica": "electronics",
            "fai da te": "diy",
            "film e tv": "dvd",
            "giardino e giardinaggio": "garden",
            "giochi e giocattoli": "toys",
            "gioielli": "jewelry",
            "grandi elettrodomestici": "appliances",
            "handmade": "handmade",
            "illuminazione": "lighting",
            "industria e scienza": "industrial",
            "informatica": "computers",
            "kindle store": "digital-text",
            "libri": "stripbooks",
            "moda": "fashion",
            "musica digitale": "digital-music",
            "orologi": "watches",
            "prima infanzia": "baby",
            "prodotti per animali domestici": "pets",
            "salute e cura della persona": "hpc",
            "scarpe e borse": "shoes",
            "software": "software",
            "sport e tempo libero": "sporting",
            "strumenti musicali e dj": "mi",
            "valigeria": "luggage",
            "videogiochi": "videogames"
        }
    },
    {
        "country": "mx",
        "categoryCodes": {
            "todos los departamentos": "aps",
            "auto": "automotive",
            "bebé": "baby",
            "dispositivos de amazon": "amazon-devices",
            "electrónicos": "electronics",
            "películas y series de tv": "dvd",
            "tienda kindle": "digital-text",
            "ropa, zapatos y accesorios": "fashion",
            "   mujeres": "fashion-womens",
            "   hombres": "fashion-mens",
            "   niñas": "fashion-girls",
            "   niños": "fashion-boys",
            "   bebé": "fashion-baby",
            "alexa skills": "alexa-skills",
            "alimentos y bebidas": "grocery",
            "deportes y aire libre": "sporting",
            "herramientas y mejoras del hogar": "hi",
            "hogar y cocina": "kitchen",
            "industria y ciencia": "industrial",
            "instrumentos musicales": "mi",
            "juegos y juguetes": "toys",
            "libros": "stripbooks",
            "mascotas": "pets",
            "música": "popular",
            "oficina y papelería": "office-products",
            "productos handmade": "handmade",
            "salud, belleza y cuidado personal": "hpc",
            "software": "software",
            "videojuegos": "videogames"
        }
    },
    {
        "country": "in",
        "categoryCodes": {
            "all categories": "aps",
            "alexa skills": "alexa-skills",
            "amazon devices": "amazon-devices",
            "amazon fashion": "fashion",
            "amazon fresh": "nowstore",
            "amazon global store": "amazon-global-store",
            "amazon pantry": "pantry",
            "appliances": "appliances",
            "apps & games": "mobile-apps",
            "baby": "baby",
            "beauty": "beauty",
            "books": "stripbooks",
            "car & motorbike": "automotive",
            "clothing & accessories": "apparel",
            "collectibles": "collectibles",
            "computers & accessories": "computers",
            "electronics": "electronics",
            "furniture": "furniture",
            "garden & outdoors": "lawngarden",
            "gift cards": "gift-cards",
            "grocery & gourmet foods": "grocery",
            "health & personal care": "hpc",
            "home & kitchen": "kitchen",
            "industrial & scientific": "industrial",
            "jewellery": "jewelry",
            "kindle store": "digital-text",
            "luggage & bags": "luggage",
            "luxury beauty": "luxury-beauty",
            "movies & tv shows": "dvd",
            "music": "popular",
            "musical instruments": "mi",
            "office products": "office-products",
            "pet supplies": "pets",
            "prime video": "instant-video",
            "shoes & handbags": "shoes",
            "software": "software",
            "sports, fitness & outdoors": "sporting",
            "tools & home improvement": "home-improvement",
            "toys & games": "toys",
            "video games": "videogames",
            "watches": "watches"
        }
    },
    {
        "country": "jp",
        "categoryCodes": {
            "すべてのカテゴリー": "aps",
            "amazon デバイス": "amazon-devices",
            "kindleストア ": "digital-text",
            "prime video": "instant-video",
            "alexaスキル": "alexa-skills",
            "デジタルミュージック": "digital-music",
            "android アプリ": "mobile-apps",
            "本": "stripbooks",
            "洋書": "english-books",
            "ミュージック": "popular",
            "クラシック": "classical",
            "dvd": "dvd",
            "tvゲーム": "videogames",
            "pcソフト": "software",
            "パソコン・周辺機器": "computers",
            "家電&カメラ": "electronics",
            "文房具・オフィス用品": "office-products",
            "ホーム&キッチン": "kitchen",
            "ペット用品": "pets",
            "ドラッグストア": "hpc",
            "ビューティー": "beauty",
            "ラグジュアリービューティー": "luxury-beauty",
            "食品・飲料・お酒": "food-beverage",
            "ベビー&マタニティ": "baby",
            "ファッション": "fashion",
            "レディース": "fashion-womens",
            "メンズ": "fashion-mens",
            "キッズ＆ベビー": "fashion-baby-kids",
            "服＆ファッション小物": "apparel",
            "シューズ＆バッグ": "shoes",
            "腕時計": "watch",
            "ジュエリー": "jewelry",
            "おもちゃ": "toys",
            "ホビー": "hobby",
            "楽器": "mi",
            "スポーツ&アウトドア": "sporting",
            "車＆バイク": "automotive",
            "diy・工具・ガーデン": "diy",
            "大型家電": "appliances",
            "クレジットカード": "financial",
            "ギフト券": "gift-cards",
            "産業・研究開発用品": "industrial",
            "amazonパントリー": "pantry",
            "amazonアウトレット": "warehouse-deals",
            "ホーム＆キッチン": "kitchen",
            "ベビー＆マタニティ": "baby",
            "スポーツ＆アウトドア": "sporting"
        }
    }
]


class ListingParser:
    def __init__(self, html):
        self.html = html
        self.d = pq(html)

    def get_title(self):
        return self.d('#productTitle').text()

    def get_tags(self):
        title = self.get_title()
        pattern = re.compile(
            r'\d+C(?:\d+A)?|\b[\d\.,]+w\b|[\d\.,]+\s?mah|\d+[\s-]?ports?|dual[\s-]?ports?|dual[\s-]?packs?|\d[\s-]?pack|\der[\s-]pack|Wireless|Built-In Lightning Connector|マグネット|コネクター|ライトニング端子一体型|Eingebaute Kabel|Built-in Cables|マグセーフ|magsafe|Built-In USB-C Connector|USB-C一体型|Magnétique|Connecteur Intégré|Built-In USB-C ケーブル|con cable|Lightning Kabel|Câbles Intégrés|magnetisch|Câbles Lightning|MagGo|タイプCコネクター|con cavo|Built-In USB-Cコネクター|Built-in Connector|Lightningコネクター|ケーブル内蔵|Magnético|Lightning Cables|Magnetic|kabellos/drahtlos|マグネティック|Magsafe|マグゴー|USB-Cケーブル一体型|MagSafe|Magnetico|Kabel',
            re.I | re.S | re.M)
        result = re.findall(pattern, title)
        return '|'.join(result)

    def get_asin(self):
        css_list = ['#ASIN']
        return self.d(','.join(css_list)).val()

    def get_brand(self):
        css_list = ['#bylineInfo']
        brand_info = self.d(','.join(css_list)).text()
        pattern = re.compile(
            'by|from|Visit the|Brand:|Marke:|Besuchen Sie den|-Store|Store|Visita lo Store di |Visita la Store de |のストアを表示|Marca: |ブランド: |Besuche den|Visiter la boutique|Marque\xa0:|De|openen|Visita la tienda de'
        )
        return re.sub(pattern, '', brand_info).strip()

    def get_ships_from(self):
        def judge_type(regex, text):
            return bool(re.findall(regex, text, re.I | re.M))

        css_list = ['#tabular-buybox', '#merchant-info', '#usedbuyBox']
        merchant_info = self.d(','.join(css_list)).text()
        # print(re.sub(r'\s+', ' ', merchant_info))
        # 与JS的差异在于: "/" ==> "'", 分组是需要加上?:，即"(" ==> "(?:"  "/gi" ==> "re.I"
        amz_regex = '(?:(?:ships|dispatched)\s+from(?:\s|\S)+sold\s+by\s+Amazon)|(?:sold\s+by:*\s+Amazon)|(?:Expédié\s+et\s+vendu\s+par\s+Amazon)|(?:Verkauf\s+und\s+Versand\s+durch\s+Amazon)|(?:Vendido\s+y\s+enviado\s+por\s+Amazon)|(?:Venduto\s+e\s+spedito\s+da\s+Amazon)|(?:Amazon.co.jp\s+が販売、発送します。)|(?:Amazon.co.jp がフラストレーション・フリー・パッケージで販売、発送します)|(?:Envío\s+desde\s+Amazon\s+México)|(?:販売元\s+Amazon.co.jp)'
        fba_regex = '(?:fulfilled|ships\s+by|from\s+Amazon)|(?:sold\s+by:)|(?:expédié\s+par\s+amazon)|(?:Versand\s+durch\s+Amazon)|(?:enviado\s+por\s+Amazon)|(?:gestionado\s+por\s+Amazon)|(?:spedito\s+da\s+Amazon)|(?:が販売し、Amazon.co.jp)|(?:Envío\s+desde\s+Amazon)|(?:出荷元\s+Amazon)'
        merch_regex = '(:?(:?ships|dispatched)\s+from\s+and\s+sold\s+by)|(:?Sold\s+by)|(:?Expédié\s+et\s+vendu\s+par)|(:?Verkauf\s+und\s+Versand\s+durch)|(:?Vendido\s+y\s+enviado\s+por)|(:?Venduto\s+e\s+spedito\s+da)|(:?^(:?(:??!Amazon.co.jp).)*?\s+が販売、発送します。)|(:?Envío\s+desde)|(:?出荷元)|(?:Spedizione)'

        amz = judge_type(amz_regex, merchant_info)
        fba = judge_type(fba_regex, merchant_info)
        merch = judge_type(merch_regex, merchant_info)

        if amz:
            ship_type = 'AMZ'
        elif fba:
            ship_type = 'FBA'
        elif merch:
            ship_type = 'FBM'
        else:
            ship_type = 'N.A.'

        return ship_type

    def get_sold_by(self):
        css_list = ['#merchant-info > a.a-link-normal:nth-of-type(1)', '#tabular-buybox a#sellerProfileTriggerId']
        merchant_info = self.d(','.join(css_list))
        return merchant_info.text()

    def get_bullet_point(self):
        # 修改list为字符串格式，方便存储
        css_list = ['#feature-bullets li:not([id]) span.a-list-item']
        return '\n'.join([re.sub('\u200f|\u200e|\xa0', ' ', i.text).strip() for i in self.d(','.join(css_list))])

    def get_price(self):
        css_list = [
            '#apex_desktop_newAccordionRow .priceToPay .a-offscreen',
            '#apex_desktop > div > .priceToPay .a-offscreen',
            '#apex_desktop > div > div > .priceToPay .a-offscreen',
            '#apex_desktop > #corePrice_desktop .apexPriceToPay .a-offscreen',
            '#apex_desktop #apex_desktop_newAccordionRow > #corePrice_desktop .apexPriceToPay .a-offscreen',
            '#apex_desktop #apex_desktop_qualifiedBuybox #corePriceDisplay_desktop_feature_div span.priceToPay span[aria-hidden="true"]',
            '#apex_desktop #apex_desktop_newAccordionRow #corePriceDisplay_desktop_feature_div span.priceToPay span[aria-hidden="true"]',
            '#apex_desktop .priceToPay .a-offscreen',
            '.priceToPay',
        ]
        price = ''
        for css in css_list:
            price = self.d(css).text()
            if price:
                break
        return re.sub(r'\s', '', price)

    def get_rating(self):
        # 评分
        css_list = ['#averageCustomerReviews_feature_div #acrPopover']
        # 海象运算符
        if rating_text := self.d(','.join(css_list)).attr('title'):
            return re.sub('5つ星のうち|\xa0étoile\(s\)', '', rating_text.split(' ')[0]).replace(',', '.')
        return ''

    def get_rating_cnt(self):
        # 实际上是global ratings
        css_list = ['#averageCustomerReviews_feature_div span#acrCustomerReviewText']
        pattern = re.compile(',|\.|\s|個の評価')
        return re.sub(pattern, '', self.d(','.join(css_list)).text().split(' ')[0])

    def get_qa(self):
        return '0'

    def get_monthly_sales(self):
        month_sale = ''
        month_sales_text = self.d('#social-proofing-faceout-title-tk_bought > span').text()
        if month_sales_text:
            slim = re.sub(
                'bought in past month|comprados el mes pasado|gekauft Mal im letzten Monat|Mal im letzten Monat gekauft|achetés au cours du mois dernier|acquistati nel mese scorso|gekocht in de afgelopen maand|kupionych w ciągu ostatniego miesiąca|köpta under den senaste månaden|satın alındı|過去1か月で|点以上購入されました|Plus de|adetten fazla|Geçen ay |\+|\s',
                '', month_sales_text)
            month_sale = slim.replace('mil', '000').replace('k', '000').replace('K', '000').replace(' ', '')
        return month_sale

    def get_listing_date(self):
        match_list = [
            'Release date',
            'Date First Available',
            'Date first available',
            'Date first listed on Amazon',
            'Date de mise en ligne sur Amazon.fr',
            'Im Angebot von Amazon.de seit',
            'Disponibile su Amazon.it a partire dal',
            'Fecha de disponibilidad en Amazon',
            'Producto en Amazon.com.mx desde',
            'Producto en Amazon.es desde',
            'Amazon.co.jp での取り扱い開始日',
            'Disponibile su Amazon.it a partire dal',
            'Datum eerste beschikbaarheid',
            'Date de mise en ligne sur Amazon.com.be'
        ]
        detail_dict = self.get_detail_dict()
        for match_text in match_list:
            tmp = detail_dict.get(match_text, '')
            if tmp:
                dt = dateparser.parse(tmp).date().__str__()
                return dt
        return ''

    def get_variant(self):
        variant_info = re.findall('"colorToAsin":(.*?),"refactorEnabled', self.html)
        if variant_info:
            try:
                variant_dict = json.loads(variant_info[0])
                return len(variant_dict) if variant_dict else 1
            except json.JSONDecodeError:
                return 1
        return 1

    def get_price_ped(self):
        css_list = ['#primeExclusivePricingMessage > a#pep-signup-link > span:nth-of-type(2)']
        return re.sub(r'\s', '', self.d(','.join(css_list)).text())

    def is_promotion(self):
        css_list = ['#applicable_promotion_list_sec']
        return bool(self.d(','.join(css_list)))

    def get_coupon(self):
        info = self.d('span[id^="couponText"]')
        if info:
            # 去掉杂乱数据，获取价格或者百分比
            tmp = re.sub('-|coupon|\xa0', '', info[0].text, flags=re.I).strip()
            for i in tmp.split():
                if re.findall(r'\d+', i):
                    return i
        return ''

    def get_video_url(self):
        video_info = re.findall(r'var obj = A\.\$\.parseJSON\(\'(.*?)\'\);', self.html)
        if not video_info:
            return ''
        url_info = re.findall(r'(https://m\.media-amazon\.com/images/S/.*?mp4)"', video_info[0])
        return url_info[0] if url_info else ''

    def get_main_img_url(self):
        css_list = ['#imgTagWrapperId img']
        return self.d(','.join(css_list)).attr('src')

    def get_color(self):
        css_list = ['.a-spacing-small.po-color td:nth-of-type(2)']
        return self.d(','.join(css_list)).text()

    # 规格：尺寸&重量
    def get_dimension(self):
        detail_dict = self.get_detail_dict()
        dimension_match_list = ['Package Dimensions', 'Product Dimensions', 'Dimensiones del producto',
                                'Dimensiones del paquete', 'Parcel Dimensions', 'Produktabmessungen',
                                'Verpackungsabmessungen', 'Dimensioni prodotto', 'Dimensioni del collo',
                                'Dimensions de l\'article L x L x H', 'Dimensions du produit (L x l x h)',
                                '製品サイズ', '梱包サイズ', 'Productafmetingen'
                                ]
        for cur_bsr_match in dimension_match_list:
            tmp = detail_dict.get(cur_bsr_match, '')
            if tmp:
                return tmp
        return ''

    def get_size(self):
        dimension = self.get_dimension()
        if dimension == '':
            css_list = ['.a-spacing-small.po-item_dimensions td:nth-of-type(2)']
            return self.d(','.join(css_list)).text()
        elif len(dimension.split(';')) == 2:
            return dimension.split(';')[0].strip()
        else:
            return dimension

    def get_weight(self):
        # con1 获取规格中的重量
        dimension = self.get_dimension()
        if len(dimension.split(';')) == 2:
            return dimension.split(';')[-1].strip()

        # con2 获取detail中的重量
        detail_dict = self.get_detail_dict()
        weight_match_list = ['Poids du produit', 'Item Weight']
        for cur_bsr_match in weight_match_list:
            tmp = detail_dict.get(cur_bsr_match, '')
            if tmp:
                return tmp

        # con3 获取简介中的重量
        css_list = ['.a-spacing-small.po-item_weight td:nth-of-type(2)']
        return self.d(','.join(css_list)).text()

    def get_manufacturer(self):
        detail_dict = self.get_detail_dict()
        manufacturer_match_list = ['Manufacturer', 'Fabricante', 'Fabricant', 'Hersteller', 'Produttore', 'メーカー',
                                   'Fabrikant']
        for cur_bsr_match in manufacturer_match_list:
            tmp = detail_dict.get(cur_bsr_match, '')
            if tmp:
                return tmp
        return ''

    def get_node_path(self):
        css_list = ['#wayfinding-breadcrumbs_feature_div']
        return self.d(','.join(css_list)).text().replace('\n', ' ')

    # 跳板(逻辑来自jungle-scout，用来获取categoryCode以调用其销量接口)
    def get_category_code_map(self):
        d = {}
        for i in self.d('#searchDropdownBox option').items():
            d[i.text().lower()] = i.val().split('=')[-1].replace('-intl-ship', '')
        return d

    # 获取详情区域(table ul)
    @lru_cache()
    def get_detail_dict(self):
        def clean(s):
            return re.sub('\u200f|\u200e', '', s).strip()

        css_list = [
            '#prodDetails tr',
            '#detailBullets_feature_div li',
            '#detailBulletsWrapper_feature_div li',
        ]
        # 由于rating废代码较多，而且在其它地方已经获取，此方法只获取其它详情
        exclude_review_pattern = re.compile('(?:reviews|media de los clientes)', re.I)
        detail_dict = {}
        for i in self.d(','.join(css_list)).items():
            if i('th').text() and not re.findall(exclude_review_pattern, i('th').text()):
                detail_dict[clean(i('th').text())] = clean(i('td').text())
            if i('li').text():
                each = i.text().split(':', 1)
                if len(each) == 2 and not re.findall(exclude_review_pattern, each[0]):
                    detail_dict[clean(each[0])] = clean(each[1])

        return detail_dict

    def get_bsr_list(self):
        link_list = []
        bsr_link_css_list = [
            '#prodDetails tr a',
            '#detailBullets_feature_div li a',
            '#detailBulletsWrapper_feature_div li a',
        ]
        for i in self.d(','.join(bsr_link_css_list)).items():
            link: str = i.attr('href')
            if 'bestsellers' in link:
                link_list.append(link)

        bsr_match_list = [
            'Amazon Bestseller',
            'Amazon Bestsellers Rank',
            'Best Sellers Rank',
            'Best-sellers rank',
            'Amazon Bestseller-Rang',
            "Classement des meilleures ventes d'Amazon",
            'Clasificación en los más vendidos de Amazon',
            'Posizione nella classifica Bestseller di Amazon',
            'Amazon 売れ筋ランキング',
            'Plaats in bestsellerlijst'
        ]
        detail_dict = self.get_detail_dict()
        for cur_bsr_match in bsr_match_list:
            bsr_info = detail_dict.get(cur_bsr_match, '')
            if bsr_info:
                li = []
                for rank_and_category in bsr_info.split('\n'):
                    rank_and_category = re.sub('\(.*?\)|\#|Nr\.|\,|\.|nº|n\.', '', rank_and_category)
                    rank = re.findall('[\d,.\s]+', rank_and_category)[0].replace(',', '').replace('.', '').replace(
                        '\xa0', '').replace('\u202f', '').strip()
                    rank_jp = re.findall('(\d+)', rank_and_category)[0].strip() if re.findall('(\d+)', rank_and_category) else -1
                    try:
                        rank_int = int(rank or rank_jp)
                    except:
                        rank_int = -1
                    cate = re.findall('(?:en|in|位|dans)(.*)', rank_and_category, re.M)[0].strip()
                    cate_jp = re.findall('(.*)(?:-)', rank_and_category, re.M)
                    li.append({
                        'category': cate or cate_jp[0].strip() if cate_jp else '',
                        'rank': rank or rank_jp,
                        'rank_int': rank_int,
                        'link': link_list.pop(0)
                    })
                return li
        return []

    def get_category_code(self, category1):
        blank_value = 'N.A.'
        category_code_map = self.get_category_code_map()
        category_code = category_code_map.get(category1.lower())
        if category_code:
            return category_code

        selected_cate_code = self.d('#searchDropdownBox option:selected').val().split('=')[-1].replace('-intl-ship', '')
        if selected_cate_code == 'aps':
            # 如果选中的是aps，去其他国家找cate1是否有对应的分类，加入没找到就直接返回选中的
            for categoryCodesForCountry in CATEGORY_CODES_BY_COUNTRY:
                category_code = categoryCodesForCountry.get(category1.lower())
                if category_code:
                    return category_code
        else:
            return selected_cate_code

        return blank_value

    def get_rank_and_category(self):
        bsr_list = self.get_bsr_list()
        if bsr_list:
            cate1 = bsr_list[0]['category']
            category_code = self.get_category_code(cate1)
            return {
                'category': cate1,
                'rank': bsr_list[0]['rank'],
                'categoryCode': category_code,
            }
        return {}

    def get_all(self):
        return {
            "asin": self.get_asin(),
            "title": self.get_title(),
            "tags": self.get_tags(),
            "bullet_point": self.get_bullet_point(),
            "price": self.get_price(),
            "price_ped": self.get_price_ped(),
            "is_promotion": self.is_promotion(),
            "coupon": self.get_coupon(),
            "variant_cnt": self.get_variant(),
            "main_img_url": self.get_main_img_url(),
            "video_url": self.get_video_url(),
            "node_path": self.get_node_path(),
            "rating": self.get_rating(),
            "rating_cnt": self.get_rating_cnt(),
            "qa_cnt": self.get_qa(),
            "monthly_sales": self.get_monthly_sales(),
            "color": self.get_color(),
            "size": self.get_size(),
            "sold_by": self.get_sold_by(),
            "ships_from": self.get_ships_from(),
            "dimension": self.get_dimension(),
            "manufacturer": self.get_manufacturer(),
            "brand": self.get_brand(),
            "weight": self.get_weight(),
            "bsr_list": self.get_bsr_list(),
            "listing_date": self.get_listing_date(),
            "rank_and_category": self.get_rank_and_category(),
        }


if __name__ == '__main__':
    asin_html = open(r"C:\Users\2577\Downloads\Amazon _ UGREEN USB Type Cケーブル PD対応 100W_5A 超急速充電 USB C ナイロン編み 断線防止 iPhone 15_16_iPad_MacBook Pro_Galaxy S24_Matebook_iPad_Xperia等USB-C各種対応(1m, ブラック) _ UGREEN _ USBケーブル 通販.html", 'r', encoding='utf-8').read()
    rp = ListingParser(asin_html)
    print(rp.get_bsr_list())


