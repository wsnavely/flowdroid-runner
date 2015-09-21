import command
import sys
import os
import os.path
import logging
import errno
import argparse

def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else: raise

outdir = "/home/ubuntu/output"
apkdir = "/home/ubuntu/apks"
platforms = "/home/ubuntu/platforms"
reporoot = "/home/ubuntu/flowdroid-runner"

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--mem")
    parser.add_argument("-o", "--s3out")
    args = parser.parse_args()

    mem = args.mem
    s3_out = args.s3out
    
    logging.basicConfig(level="DEBUG")
    log_dir = os.path.join(outdir, "log")
    flowdroid_dir = os.path.join(outdir, "flowdroid")
    mkdir_p(log_dir)
    mkdir_p(flowdroid_dir)

    for apk in os.listdir(apkdir):
        if not apk.endswith(".apk"):
            continue
        apk_path = os.path.join(apkdir, apk)
        apk_name = os.path.basename(apk_path)
        fd_log = os.path.join(log_dir, apk_name + "_flowdroid")
        fd_out = os.path.join(flowdroid_dir, (apk_name + ".xml"))

        logging.info("Processing APK: " + apk_path)
        args = ["-Xmx" + mem] 
        args += ["-jar", os.path.join(reporoot, "didfail_phase1.jar")]
        args += ["-apk", apk_path]
        args += ["-platforms", platforms]
        args += ["-out", fd_out]
        args += ["-config", os.path.join(reporoot, "didfail.json")]
        args += ["-ss", os.path.join(reporoot, "SourcesAndSinks.txt")]
        args += ["-tw", os.path.join(reporoot, "EasyTaintWrapperSource.txt")]
        
        cmd = command.Command("/usr/bin/java", args, stdout=fd_log, stderr=fd_log)
	cmd.run(60*15)

    s3_cmd = "s3cmd sync " + outdir + " " + s3_out
    os.system(s3_cmd)    
