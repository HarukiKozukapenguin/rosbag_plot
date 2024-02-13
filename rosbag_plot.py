#!/usr/bin/env python

import rosbag
import numpy as np
import sys
import os
import matplotlib.pyplot as plt
import yaml
from typing import List, Dict

class bagLoader:
    def __init__(self, obj):
        self.bag_filename = os.path.join(os.getcwd(), obj["bag_filename"])
        self.bag = rosbag.Bag(self.bag_filename)
        self.robot_ns = obj["robot_ns"]
        self.plot_topic_names = obj["plot_topic_names"]
        for i in range(len(self.plot_topic_names)):
            self.plot_topic_names[i] = "/" + self.robot_ns + "/" + self.plot_topic_names[i]

        self.plot_fields = obj["plot_fields"]
        self.plot_colors = obj["plot_colors"]
        self.start_time = obj["start_time"]
        self.end_time = obj["end_time"]
        self.show_legend = obj["show_legend"]
        self.legends = []
#         if(self.show_legend):
        self.legends = obj["legends"]
        self.x_label = obj["x_label"]
        self.y_label = obj["y_label"]
        self.y_range = obj["y_range"]

        print("bag_filename: ", self.bag_filename)
        print("robot_ns: ", self.robot_ns)
        print("plot_topic_names", self.plot_topic_names)
        print("plot_fields: ", self.plot_fields)
        print("start_time: ", self.start_time)
        print("end_time: ", self.end_time)

        # get initial time in rosbag
        self.zero_time = 0
        for i, (topic, msg, t) in enumerate(self.bag.read_messages("/" + self.robot_ns + "/flight_state")):
            if(i == 0):
                self.zero_time = t.secs + t.nsecs / 1000000000.0
        print("zero time: ", self.zero_time)

        # get data from rosbag
        self.datas = [np.empty(0)] * len(self.plot_topic_names)
        self.times = [np.empty(0)] * len(self.plot_topic_names)

        for i, (topic, msg, t) in enumerate(self.bag.read_messages(topics = self.plot_topic_names)):
            for j in range(len(self.plot_topic_names)):
                if(self.plot_topic_names[j] == topic):
                    plot_field = self.plot_fields[j]
                    plot_field_attribs = plot_field.split("/")
                    data = msg
                    for plot_field_attrib in plot_field_attribs:
                        data = getattr(data, plot_field_attrib)

                    rosbag_time = t.secs + t.nsecs / 1000000000.0 - self.zero_time
                    if(self.start_time <= rosbag_time and rosbag_time <= self.end_time):
                        self.datas[j] = np.append(self.datas[j], data)
                        self.times[j] = np.append(self.times[j], rosbag_time - self.start_time)

class bagPlotter:
    def __init__(self, bag_data_list: List[Dict[bagLoader, Dict]]):
        obj = bag_data_list[0]["obj"]

        self.fig = plt.figure(figsize=obj["fig_size"])
        
        for i, bag_yaml_data in enumerate(bag_data_list):
            print("type(bag_yaml_data): ", type(bag_yaml_data))
            print("bag_yaml_data.keys(): ",bag_yaml_data.keys())
            data_dim:int = np.ceil(np.sqrt(len(bag_data_list)))
            self.plot_bag_data(length = data_dim, number = i, **bag_yaml_data)

        if(obj["save_fig"]):
            plt.savefig(obj["save_fig_name"])
        else:
            plt.show()

    def plot_bag_data(self, length: int, number: int, bag_data: bagLoader, obj: Dict): #ax is type of np.array, which includes matplotlib.axes
        # plot data
        plt.rcParams['font.family'] = 'Times New Roman' # https://kenbo.hatenablog.com/entry/2018/11/28/111639
        plt.rcParams['figure.subplot.bottom'] = 0.2     # https://qiita.com/78910jqk/items/e8bce993081c384afdba
        print("length of plot: ", len(bag_data.plot_topic_names))
        print("length of times: ", len(bag_data.times))
        print("length of datas: ", len(bag_data.datas))
        print("length of colors: ", len(bag_data.plot_colors))
        print("length of legends: ", len(bag_data.legends))

        print("length: ",length)
        print("number: ",number)
        ax = self.fig.add_subplot(length,length,number + 1)

        for i in range(len(bag_data.plot_topic_names)):
            ax.plot(bag_data.times[i], bag_data.datas[i], color=bag_data.plot_colors[i], label=bag_data.legends[i], linewidth = obj["width"])
        if(bag_data.show_legend):
            ax.legend(frameon=False, fontsize=obj["legend_fontsize"])
        ax.set_xlabel(bag_data.x_label, fontsize=obj["x_label_fontsize"])
        ax.set_ylabel(bag_data.y_label, fontsize=obj["y_label_fontsize"])
        ax.set_ylim(bag_data.y_range)
        ax.tick_params(labelsize=obj["label_fontsize"])


if __name__ == "__main__":
    length_argv = len(sys.argv)
    config_path_list = [""]*(length_argv-1)
    if(length_argv >= 2):
        for i in range(length_argv-1):
            config_path_list[i] = sys.argv[i+1]
        print("config_path_list: ", config_path_list)

    else:
        print("Please specify the config file name!")
        sys.exit()

    bag_data_list = []
    for config_path in config_path_list:
         with open(config_path) as file:
            obj: Dict = yaml.safe_load(file)
            bag_data = bagLoader(obj)
            bag_data_list.append({"bag_data": bag_data, "obj": obj})

    bagPlotter(bag_data_list)
