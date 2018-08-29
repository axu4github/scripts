# coding=utf-8

from doraemon import Doraemon
import os
import sys


class TransferVoiceAnnotationFiles(object):

    def get_tagfiles(self, input_dir):
        return Doraemon.get_files_by_suffix(input_dir, ".tag")

    def transfer_tagfile(self, tagfile_path,
                         in_charset=None, out_charset=None):
        transferred = []
        lines = Doraemon.get_file_contents(
            tagfile_path, in_charset=in_charset, out_charset=out_charset)
        for line in lines:
            line = line.split(" ")
            try:
                if len(line) < 4 or line[1].startswith("0"):
                    continue
            except Exception:
                continue

            transferred.append(line[-1])

        return transferred

    def save_transferred(self, raw_fname, transferred, output_dir=None):
        output_fpath = "transferred_{0}.txt".format(
            os.path.splitext(os.path.basename(raw_fname))[0])
        if output_dir is not None:
            if not os.path.isdir(output_dir):
                os.makedirs(output_dir)

            output_fpath = os.path.join(output_dir, output_fpath)

        return (
            Doraemon.put_file_contents(output_fpath, transferred),
            output_fpath
        )


if __name__ == "__main__":
    input_dir = sys.argv[1]
    output_dir = sys.argv[2]
    tvaf = TransferVoiceAnnotationFiles()
    tagfiles = tvaf.get_tagfiles(input_dir)
    for tagfile in tagfiles:
        transferred = tvaf.transfer_tagfile(
            tagfile, in_charset="gbk", out_charset="utf-8")
        tvaf.save_transferred(tagfile, transferred, output_dir=output_dir)
