#!/usr/bin/env python

import rosbag
import numpy as np
import sys
import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import yaml
from typing import List, Dict

class bagLoader:
    def __init__(self, obj):
        self.bag_filename = os.path.join(os.getcwd(), "bag_data/", obj["bag_filename"])
        self.bag = rosbag.Bag(self.bag_filename)
        self.robot_ns = obj["robot_ns"]
#        self.plot_topic_names = obj["plot_topic_names"]
#        for i in range(len(self.plot_topic_names)):
#            self.plot_topic_names[i] = "/" + self.robot_ns + "/" + self.plot_topic_names[i]

        self.plot_x_y_topic_names = obj["plot_x_y_topic_names"]
        self.plot_x_topic_names = "/" + self.robot_ns + "/" + self.plot_x_y_topic_names[0]
        self.plot_y_topic_names = "/" + self.robot_ns + "/" + self.plot_x_y_topic_names[1]

#        self.plot_fields = obj["plot_fields"]

        self.plot_x_y_fields = obj["plot_x_y_fields"]
        self.plot_x_fields = self.plot_x_y_fields[0]
        self.plot_y_fields = self.plot_x_y_fields[1]

        self.plot_colors = obj["plot_colors"]
        self.start_time = obj["start_time"]
        self.end_time = obj["end_time"]
        self.show_legend = obj["show_legend"]
        self.legends = []
#         if(self.show_legend):
        self.legends = obj["legends"]
#       self.one_d_x_label = obj["one_d_x_label"]
#       self.one_d_y_label = obj["one_d_y_label"]
#       self.one_d_y_range = obj["one_d_y_range"]

        self.two_d_x_label = obj["x_label"]
        self.two_d_y_label = obj["y_label"]
        self.two_d_x_range = obj["x_range"]
        self.two_d_y_range = obj["y_range"]
        self.x_shift = obj["x_shift"]
        self.y_shift = obj["y_shift"]

        self.obstacle_pos = obj["obstacle_position"]
        self.radius = obj["obstacle_radius"]

        print("bag_filename: ", self.bag_filename)
        print("robot_ns: ", self.robot_ns)
        print("start_time: ", self.start_time)
        print("end_time: ", self.end_time)

        # get initial time in rosbag
        self.zero_time = 0
        for i, (topic, msg, t) in enumerate(self.bag.read_messages("/" + self.robot_ns + "/flight_state")):
            if(i == 0):
                self.zero_time = t.secs + t.nsecs / 1000000000.0
        print("zero time: ", self.zero_time)

        # get data from rosbag
        self.datas = np.empty(0)
        self.times = np.empty(0)

        self.x_datas = np.empty(0)
        self.y_datas = np.empty(0)

        for i, ((x_topic, x_msg, x_t), (y_topic, y_msg, y_t)) in enumerate(\
                    zip(self.bag.read_messages(topics = self.plot_x_topic_names),
                        self.bag.read_messages(topics = self.plot_y_topic_names))):
            if(self.plot_x_topic_names == x_topic):
                plot_x_field = self.plot_x_fields
                plot_x_field_attribs = plot_x_field.split("/")
#                print("x_msg: ", x_msg)
                x_data = x_msg
            if(self.plot_y_topic_names == y_topic):
                plot_y_field = self.plot_y_fields
                plot_y_field_attribs = plot_y_field.split("/")
                y_data = y_msg
                
            for plot_x_field_attrib, plot_y_field_attrib in zip(plot_x_field_attribs, plot_y_field_attribs):
#                print("plot_x_field_attrib, plot_y_field_attrib: ",\
#                      plot_x_field_attrib, plot_y_field_attrib)
                x_data = getattr(x_data, plot_x_field_attrib)
                y_data = getattr(y_data, plot_y_field_attrib)

            rosbag_time = x_t.secs + x_t.nsecs / 1000000000.0 - self.zero_time
            if(self.start_time <= rosbag_time and rosbag_time <= self.end_time):
                self.x_datas = np.append(self.x_datas, x_data + self.x_shift)
                self.y_datas = np.append(self.y_datas, y_data + self.y_shift)

class bagPlotter:
    def __init__(self, bag_data_dict: Dict[Dict, bagLoader]):
        obj = bag_data_dict["obj"]

        plt.rcParams['figure.subplot.bottom'] = 0.20
        self.fig = plt.figure(figsize=obj["fig_size"])
        bag_data = bag_data_dict["bag_data"]

#        bag_data_num = self.calc_bag_data_num(bag_data_list)
#        data_dim:int = np.ceil(np.sqrt(bag_data_num))

#        for i, bag_yaml_data in enumerate(bag_data_list):
#            self.time_series_plot_bag_data(length = data_dim, number = 2*i, **bag_yaml_data)
        self.ax = self.fig.subplots()
        self.ax.minorticks_on()
        self.ax.grid(which = "both", alpha=0.4)
        self.x_y_plot_bag_data(bag_data, obj)
        self.plot_obstacles(bag_data)

        if(obj["save_fig"]):
            plt.savefig(obj["save_fig_name"])
        else:
            plt.show()

    def calc_bag_data_num(self, bag_data_list: List[Dict[bagLoader, Dict]]):
        num_plot = 0
        for i, bag_yaml_data in enumerate(bag_data_list):
            num_plot += len(bag_yaml_data["bag_data"].plot_topic_names) + len(bag_yaml_data["bag_data"].plot_x_y_topic_names)
        return num_plot

    def time_series_plot_bag_data(self, length: int, number: int, bag_data: bagLoader, obj: Dict): #ax is type of np.array, which includes matplotlib.axes
        # plot data
#        plt.rcParams['font.family'] = 'Times New Roman' # https://kenbo.hatenablog.com/entry/2018/11/28/111639
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
#       ax.set_xlabel(bag_data.one_d_x_label, fontsize=obj["one_d_x_label_fontsize"])
#       ax.set_ylabel(bag_data.one_d_y_label, fontsize=obj["one_d_y_label_fontsize"])
#       ax.set_ylim(bag_data.one_d_y_range)
        ax.tick_params(labelsize=obj["label_fontsize"])

    def x_y_plot_bag_data(self, bag_data: bagLoader, obj: Dict): #ax is type of np.array, which includes matplotlib.axes

#        for i in range(len(bag_data.plot_topic_names)):
        self.ax.plot(bag_data.x_datas, bag_data.y_datas, color=bag_data.plot_colors, label=bag_data.legends, linewidth = obj["width"])
        if(bag_data.show_legend):
            self.ax.legend(frameon=False, fontsize=obj["legend_fontsize"])
        self.ax.set_xlabel(bag_data.two_d_x_label, fontsize=obj["x_label_fontsize"])
        self.ax.set_ylabel(bag_data.two_d_y_label, fontsize=obj["y_label_fontsize"])
        self.ax.set_xlim(bag_data.two_d_x_range)
        self.ax.set_ylim(bag_data.two_d_y_range)
        self.ax.tick_params(labelsize=obj["label_fontsize"])

    def plot_obstacles(self, bag_data: bagLoader):
        obstacle_pos = bag_data.obstacle_pos
        obstacle_radius = bag_data.radius
        for pos in obstacle_pos:
            c = patches.Circle(xy=(pos[0], pos[1]), radius=obstacle_radius, fc='orange')
            self.ax.add_patch(c)

if __name__ == "__main__":
#    length_argv = len(sys.argv)
#    config_path_list = [""]*(length_argv-1)
    config_path = sys.argv[1]
#   if(length_argv >= 2):
#       for i in range(length_argv-1):
#           config_path_list[i] = sys.argv[i+1]
#       print("config_path_list: ", config_path_list)

    if len(sys.argv) == 1:
        print("Please specify the config file name!")
        sys.exit()

#    for config_path in config_path_list:
    with open(config_path) as file:
        obj: Dict = yaml.safe_load(file)
        bag_data = bagLoader(obj)
#        bag_data_list.append({"bag_data": bag_data, "obj": obj})

    bagPlotter({"obj": obj, "bag_data": bag_data})
