import rethinkdb as r
from datetime import datetime
from hashlib import md5
from scrapy import log


class FractionPipeline(object):

    def process_item(self, item, spider):
        item['totals']['points'] = item['totals']['points'].replace("ov ","").replace("\xc2\xbd",".5") # \xc2\xbd = 1/2
        item['spreads']['hdp'] = item['spreads']['hdp'].replace("PK","0").replace("\xc2\xbd",".5").replace("-.5","-0.5").replace("+.5","+0.5")
        return item

class RethinkdbPipeline(object):

    conn = None
    rethinkdb_settings = {}

    @classmethod
    def from_crawler(cls, crawler):
        settings = crawler.settings

        rethinkdb_settings = settings.get('RETHINKDB', {})

        return cls(rethinkdb_settings)

    def __init__(self, rethinkdb_settings):
        self.rethinkdb_settings = rethinkdb_settings

    def open_spider(self, spider):
        if self.rethinkdb_settings:
            self.table_name = self.rethinkdb_settings.pop('table_name')
            self.db_name = self.rethinkdb_settings['db']
            self.conn = r.connect(**self.rethinkdb_settings)
            table_list = r.db(self.db_name).table_list().run(
                self.conn
            )
            if self.table_name not in table_list:
                r.db(self.db_name).table_create(self.table_name).run(self.conn)

    def close_spider(self, spider):
        if self.conn:
            self.conn.close()

    def process_item(self, item, spider):
	item['UUID'] = self._get_uuid(item)
        if self.conn:
            result=r.table(self.table_name).insert(item,return_changes=True,conflict='update').run(self.conn)
            if result['unchanged']==0:
                log.msg(result,level=log.INFO,spider=spider)
        return item

    def _get_uuid(self, item):
        return md5((item['homeTeam']+item['awayTeam'])).hexdigest()

