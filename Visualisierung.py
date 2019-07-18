import pandas as pd
import os
import matplotlib.pyplot as plt

path = "/home/standardheld/Benchmark/CONFIGS/"

export_path = "/home/standardheld/Benchmark/Metriken/"

metric_path = "/home/standradheld/Benchmark/Metriken/"

def get_files(path):
    file_list = []
    for filename in os.listdir(path):
        file_list.append(filename)
    return file_list

def create_metric(path, file, export_path,project):
    metric = pd.read_json(path + file, orient="records")
    metric_type = ""
    if "container" in file:
        metric_type = "container"
        try:
            # Create target Directory
            os.mkdir(export_path + project)
        except FileExistsError:
            print("Directory ", str(export_path+"/container/"), " already exists")
            try:
                # Create target Directory
                os.mkdir(export_path + project + "/container/")
            except FileExistsError:
                print("Directory ", str(export_path + "/container/"), " already exists")
    elif "node" in file:
        metric_type ="node"
        try:
            # Create target Directory
            os.mkdir(export_path + project)
        except FileExistsError:
            print("Directory ", str(export_path+"/node/"), " already exists")
            try:
                # Create target Directory
                os.mkdir(export_path + project + "/node/")
            except FileExistsError:
                print("Directory ", str(export_path + "/node/"), " already exists")
    else:
        metric_type="unknown"

    #print(metric_type)
    data = metric["json"]
    result = data.to_dict()
    result = result["data"]
    result = result["result"]
    name = ""
    service=""
    id=""

    if metric_type == "container":# or metric_type == "node":
        frame = pd.DataFrame()
        first = True
        for metric_chunk in result:
            #print(metric_chunk)
            metric = metric_chunk["metric"]
            #print(metric)
            values = metric_chunk["values"]


            try:
                if metric_type == "container":
                    service = metric["container_label_com_docker_swarm_service_name"]
                    id = metric["container_label_com_docker_swarm_service_id"]
                    name = metric["__name__"]
            except:
                break

            chunks = {}
            chunks["Time"] = []
            chunks[service] = []
            for value_chunk in values:
                time= value_chunk[0]
                time_value = value_chunk[1]
                chunks["Time"].append(time)
                chunks[service].append(time_value)
            sub_frame = pd.DataFrame(chunks)
            sub_frame["Time"] = pd.to_datetime(sub_frame["Time"], unit='s')
            sub_frame.set_index("Time", inplace=True)
            #print(sub_frame)
            if first:
                frame = sub_frame
                first = False
            else:
                frame = pd.concat([frame,sub_frame], axis=1)
        export_path = export_path# +project
        path = export_path + project +"/"+metric_type + "/" + project + "_" + file.split(".")[0] + "/" + name + ".csv"
        #print(path)
        try:
            # Create target Directory
            new_path = export_path + project+ "/"+metric_type + "/" + project + "_" + file.split(".")[0]
            os.mkdir(new_path)
        except FileExistsError:
            print("Directory ", str(new_path), " already exists")
        frame = frame.groupby(frame.columns, axis=1).first()
        print(frame)
        export_csv(frame, path)
        frame = frame.astype(float)
        try:
            plt.figure()
            frame.plot(title=name)
            plt.savefig(path + ".png")
        except:
            print("Unable to plot")

def export_csv(frame, path):
    frame.to_csv(path)

def create_metrics():
    files = get_files(path)

    useful_metrics = []

    for file in files:
        try:
            # Create target Directory
            os.mkdir(export_path + file)
        except FileExistsError:
            print("Directory ", str(export_path + file), " already exists")
        metric_files = get_files(path + file + "/metric")
        for metric_file in metric_files:
            metric = create_metric(path + file + "/metric/", metric_file, export_path, file)


create_metrics()


#frame = pd.DataFrame(data=result,columns=["Time","HttpsRequests"])

#print(frame)