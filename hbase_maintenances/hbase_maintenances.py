# coding=utf-8

from hbase_client import HBaseClient
from solrcloud_client import SolrCloudClient
from utils import Utils
from configs import Config
import click
import os
import sys
reload(sys)
sys.setdefaultencoding("utf-8")


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
    if row_key is not None:
        HBaseClient(Config.HBASE_HOST, Config.HBASE_TABLE).delete(row_key)
    elif query is not None:
        if srf is None:
            srf = Config.DEFAULT_SOLR_RESULT_FILE

        if SolrCloudClient(Config.SOLR_NODES).download(
                query, srf, fl="id"):
            deleted_file = Utils.get_deleted_filepath(srf)
            start_number = 1
            if os.path.exists(deleted_file) and os.path.isfile(deleted_file):
                start_number = Utils.get_file_line_number(deleted_file)

            HBaseClient(
                Config.HBASE_HOST, Config.HBASE_TABLE).delete_from_file(
                    srf, start=start_number)
    else:
        pass


if __name__ == "__main__":
    cli()
