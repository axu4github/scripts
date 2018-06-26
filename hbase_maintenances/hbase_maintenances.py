# coding=utf-8

from hbase_client import HBaseClient
from solrcloud_client import SolrCloudClient
from utils import Utils
from configs import Config
from loggings import LoggableMixin
import click
import os
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

logging = LoggableMixin()


@click.group(context_settings=Config.CLICK_CONTEXT_SETTINGS)
@click.help_option("-h", "--help", help="使用说明")
def cli():
    """
    HBase 维护脚本

    获取帮助信息请执行 python hbase_maintenances.py --help
    """
    pass


@cli.command(short_help="删除数据")
@click.help_option("-h", "--help", help="使用说明")
@click.option("--row_key", default=None, help="按照给定的 ROW KEY 删除数据")
@click.option("--query", default=None, help="按照给定的 SOLR QUERY 删除数据")
@click.option("--srf", default=None, help="Solr 查询结果文件（Solr Result File）")
def delete(row_key=None, query=None, srf=None):
    logging.logger.info("Start Delete")
    hbase_client = HBaseClient(Config.HBASE_HOST, Config.HBASE_TABLE)
    if row_key is not None:
        hbase_client.delete(row_key)
        logging.logger.info("Finish Delete RowKey[{0}]".format(row_key))
    elif query is not None:
        if srf is None:
            srf = Utils.get_solr_result_filepath(query)

        solrcloud_client = SolrCloudClient(Config.SOLR_NODES)
        logging.logger.info(
            """
            Start Download Solr Data By Query: [{0}] To Result File: [{1}]
            """.format(query, srf).strip())
        if solrcloud_client.download(
                query, srf, fl="id"):
            logging.logger.info(
                "Finish Download Solr Data To File: [{0}]".format(srf))
            deleted_file = Utils.get_deleted_filepath(srf)
            start_number = 1
            if os.path.exists(deleted_file) and os.path.isfile(deleted_file):
                start_number = Utils.get_file_line_number(deleted_file)

            logging.logger.info(
                "Start Delete Hbase Data By Query[{0}]".format(query))
            hbase_client.delete_from_file(srf, start=start_number)
            logging.logger.info(
                "Finish Delete Hbase Data By Query[{0}]".format(query))

            logging.logger.info(
                "Start Delete Solr Data By Query[{0}]".format(query))
            solrcloud_client.delete(query=query)
            logging.logger.info(
                "Finish Delete Solr Data By Query[{0}]".format(query))
    else:
        raise Exception("Delete RowKey or Query Not Set.")


if __name__ == "__main__":
    cli()
