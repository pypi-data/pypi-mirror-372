import re
from functools import lru_cache

from dateparser.search import search_dates
from pyquery import PyQuery as pq


class ReviewExtractor:
    site_alias = {
        "US": [
            "United States",
            "Vereinigten Staaten",
            "美国",
            "アメリカ合衆国",
            "Estados Unidos",
            "Estados Unidos",
            "États-Unis",
            "Stati Uniti"
        ],
        "JP": [
            "Japan",
            "Japan",
            "日本",
            "日本",
            "Japón",
            "Japão",
            "Japon",
            "Giappone"
        ],
        "DE": [
            "Germany",
            "Deutschland",
            "德国",
            "ドイツ",
            "Alemania",
            "Alemanha",
            "Allemagne",
            "Germania"
        ],
        "UK": [
            "United Kingdom",
            "Vereinigten Königreich",
            "英国",
            "英国",
            "Reino Unido",
            "Reino Unido",
            "Royaume-Uni",
            "Regno Unito"
        ],
        "FR": [
            "France",
            "Frankreich",
            "法国",
            "フランス",
            "Francia",
            "França",
            "France",
            "Francia"
        ],
        "IT": [
            "Italy",
            "Italien",
            "意大利",
            "イタリア",
            "Italia",
            "Itália",
            "Italie",
            "Italia"
        ],
        "ES": [
            "Spain",
            "Spanien",
            "西班牙",
            "スペイン",
            "España",
            "Espanha",
            "Espagne",
            "Spagna"
        ],
        "CA": [
            "Canada",
            "Kanada",
            "加拿大",
            "カナダ",
            "Canadá",
            "Canadá",
            "Canada",
            "Canada"
        ],
        "IN": [
            "India",
            "Indien",
            "印度",
            "インド",
            "India",
            "Índia",
            "Inde",
            "India"
        ],
        "MX": [
            "Mexico",
            "Mexiko",
            "墨西哥",
            "メキシコ",
            "México",
            "México",
            "Mexique",
            "Messico"
        ],
        "AU": [
            "Australia",
            "Australien",
            "澳大利亚",
            "オーストラリア",
            "Australia",
            "Austrália",
            "Australie",
            "Australia"
        ],
        "AE": [
            "阿联酋"
        ],
        "NL": [
            "Netherlands",
            "Niederlanden",
            "荷兰",
            "オランダ",
            "Países Bajos",
            "Países Baixos",
            "Pays-Bas",
            "Paesi Bassi"
        ],
        "SE": [
            "Sweden",
            "瑞典"
        ],
        "SA": [
            "Saudi Arabia",
            "沙特阿拉伯",
        ],
        "SG": [
            "Singapore",
            "Singapur",
            "新加坡",
            "シンガポール",
            "Singapur",
            "Singapura",
            "Singapour",
            "Singapore"
        ]
    }
    amazon_host_mapping = {
        'US': 'www.amazon.com',
        'UK': 'www.amazon.co.uk',
        'DE': 'www.amazon.de',
        'FR': 'www.amazon.fr',
        'IT': 'www.amazon.it',
        'JP': 'www.amazon.co.jp',
        'CA': 'www.amazon.ca',
        'MX': 'www.amazon.com.mx',
        'ES': 'www.amazon.es',
        'IN': 'www.amazon.in',
        'AU': 'www.amazon.com.au',
        'AE': 'www.amazon.ae',
        'NL': 'www.amazon.nl',
        'SE': 'www.amazon.se',
        'SA': 'www.amazon.com.sa',
        'SG': 'www.amazon.com.sg'
    }

    def __init__(self, html, asin=''):
        self.html = html
        self.d = pq(self.html.replace('\\n', '').replace("\n", '').replace('\\', ''))
        self.asin = asin

    @classmethod
    @lru_cache()
    def get_nations_pattern(cls):
        """将所有的国家词汇放入一个pattern中"""
        nation_li = []
        for _, value in cls.site_alias.items():
            nation_li.extend(value)
        return '|'.join(set(nation_li))

    def get_site(self, nation_name):
        # 根据匹配到的国家信息获取其站点简称，以区分站点及获取评论链接
        for site, alias in self.site_alias.items():
            if nation_name in alias:
                return site
        return None

    def get_country_and_date(self, dom):
        # 获取评论的国家和日期
        blank_value = 'N.A.'
        country_and_date = dom('[data-hook="review-date"]').text()
        # TODO: 各国语言配置可能不对
        languages = ['de', 'en', 'fr', 'ja', 'it', 'zh', 'es']
        comment_date_match = search_dates(country_and_date, languages=languages)
        if comment_date_match:
            comment_date = comment_date_match[0][1].strftime('%Y-%m-%d')
        else:
            comment_date = blank_value
        country_info = re.findall(self.get_nations_pattern(), country_and_date)
        if country_info:
            # TODO: 此处国家匹配可能缺失，get_site
            country = self.get_site(country_info[0])
        else:
            country = blank_value

        return country, comment_date

    def get_comment_qty(self):
        text = self.d('#filter-info-section').text()
        review_text = re.findall(r'([\d,.]+)', text)
        if review_text:
            return int(review_text[-1].replace(',', '').replace('.', ''))

    def parse_all(self):
        li = []
        for each in self.d('li[id][data-hook="review"]').items():
            comment_id = each.attr('id')
            title = each('[data-hook="review-title"] > span').text()
            content = each('span[data-hook="review-body"]').text()
            vp = '是' if each('span[data-hook="avp-badge"]') else '否'
            variant = each('a[data-hook="format-strip"]').text()
            asin = re.findall('product-reviews/(.*?)/', each('a[data-hook="format-strip"]').attr('href'))[
                0] if variant else self.asin
            rating = each('i[data-hook*="review-star-rating"]').text()[0]
            helpful_info = re.findall(r'[\d,.]+', each('span[data-hook="helpful-vote-statement"]').text())
            helpful = helpful_info[0] if helpful_info else 0
            name = each('.a-profile-name').text()
            country, comment_date = self.get_country_and_date(each)
            # 修复因国家没解析出来而导致的评论链接错误
            comment_url = 'https://{}/gp/customer-reviews/{}'.format(self.amazon_host_mapping[country],
                                                                     comment_id) if country != 'N.A.' else ''

            item = {
                'asin': asin,
                'comment_id': comment_id,
                'variant': variant,
                'name': name,
                'title': title,
                'content': content,
                'vp': vp,
                'rating': rating,
                'helpful': helpful,
                'comment_date': comment_date,
                'country': country,
                'comment_url': comment_url
            }
            li.append(item)
        return li


if __name__ == '__main__':
    html = open(r"C:\Users\lonely\OneDrive\桌面\评论解析.html", 'r', encoding='utf-8').read()
    parser = ReviewExtractor(html)
    for i in parser.parse_all():
        print(i)
