
import os
import imageio
from optparse import OptionParser


def jpgToGif(jpg_dir, gif_path):
    filenames = sorted((fn for fn in os.listdir(jpg_dir) if fn.endswith('.jpg')))
    with imageio.get_writer(gif_path, mode='I') as writer:
        for filename in filenames:
            writer.append_data(imageio.imread(jpg_dir + "\\" + filename))


if __name__ == '__main__':
    parser = OptionParser()

    parser.add_option("-d", "--datadir",
                      dest="dataDir",
                      type="string",
                      help="input datadir")

    parser.add_option("-o", "--output",
                      dest="outFile",
                      type="string",
                      help="Output File Name")

    (options, args) = parser.parse_args()
    jpgDir = options.dataDir
    print(jpgDir)
    gifPath = options.outFile
    print(gifPath)
    jpgToGif(jpgDir, gifPath)
    print("Done!")

