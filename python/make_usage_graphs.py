import glob
import os
import matplotlib.pyplot as plt
from PIL import Image


def merge_photos(photo1, photo2, output):
    images = [Image.open(x) for x in [photo1, photo2]]
    widths, heights = zip(*(i.size for i in images))

    total_width = sum(widths)
    max_height = max(heights)

    new_im = Image.new('RGB', (total_width, max_height))

    x_offset = 0
    for im in images:
        new_im.paste(im, (x_offset, 0))
        x_offset += im.size[0]

    new_im.save(output)


root_dir = '/home/igor/test_output'
file_usage_paths = glob.glob(root_dir + "/*usage*")
for file_usage_path in file_usage_paths:
    if file_usage_path.split('.')[-1] == "png":
        continue
    filename = file_usage_path.split('/')[-1]
    lsvm_type = filename.split('_')[0]
    dataset_name = filename.split('_')[1]
    filename_prefix = lsvm_type + '_' + dataset_name
    filename_suffix = filename.split('_')[2].split('.')[0]

    cpu_usage_output_filename = filename_prefix + "_cpu_" + filename_suffix + ".png"
    mem_usage_output_filename = filename_prefix + "_mem_" + filename_suffix + ".png"
    merged_usage_output_filename = filename_prefix + "_cpu_mem_" + filename_suffix + ".png"

    cpu_usage_output_filepath = os.path.join(root_dir, cpu_usage_output_filename)
    mem_usage_output_filepath = os.path.join(root_dir, mem_usage_output_filename)
    merged_usage_output_filepath = os.path.join(root_dir, merged_usage_output_filename)

    cpu_usage = []
    mem_usage = []
    with open(file_usage_path) as file:
        data = file.readlines()
        for line in data:
            line = line.rstrip("\n")
            line = line.split(' ')
            cpu_usage.append(float(line[0]))
            mem_usage.append(float(line[1]))

    plt.figure()
    plt.plot(cpu_usage)
    plt.title(lsvm_type + ' ' + dataset_name + ' - CPU usage')
    plt.ylabel("CPU usage (%)")
    plt.xlabel("seconds (s)")
    plt.savefig(cpu_usage_output_filepath)
    plt.close()

    plt.figure()
    plt.plot(mem_usage)
    plt.title(lsvm_type + ' ' + dataset_name + ' - MEM usage')
    plt.ylabel("MEM usage (%)")
    plt.xlabel("seconds (s)")
    plt.savefig(mem_usage_output_filepath)
    plt.close()

    merge_photos(cpu_usage_output_filepath, mem_usage_output_filepath, merged_usage_output_filepath)

