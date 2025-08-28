import PySpin

def get_camera_model_name():
    system = PySpin.System.GetInstance()
    cam_list = system.GetCameras()

    if cam_list.GetSize() == 0:
        print("No camera detected.")
        system.ReleaseInstance()
        return

    cam = cam_list.GetByIndex(0)
    nodemap_tldevice = cam.GetTLDeviceNodeMap()

    device_model_node = PySpin.CStringPtr(nodemap_tldevice.GetNode("DeviceModelName"))
    if PySpin.IsAvailable(device_model_node) and PySpin.IsReadable(device_model_node):
        print("Camera model:", device_model_node.GetValue())
    else:
        print("Could not read device model name.")

    cam_list.Clear()
    system.ReleaseInstance()

get_camera_model_name()
