import PySpin
import cv2
import numpy as np
import argparse
def set_camera_settings(cam, exposure, gain):
    nodemap = cam.GetNodeMap()

    # Set pixel format to Mono8 if available and writable
    pixel_format_node = PySpin.CEnumerationPtr(nodemap.GetNode("PixelFormat"))
    mono8_entry = pixel_format_node.GetEntryByName("Mono8")

    if (PySpin.IsAvailable(mono8_entry) and PySpin.IsReadable(mono8_entry)
            and PySpin.IsWritable(pixel_format_node)):
        pixel_format_node.SetIntValue(mono8_entry.GetValue())
        print("Set camera output to Mono8")
    else:
        print("PixelFormat not writable or Mono8 not available. Skipping pixel format change.")

    # Set exposure
    exposure_auto = PySpin.CEnumerationPtr(nodemap.GetNode("ExposureAuto"))
    exposure_time = PySpin.CFloatPtr(nodemap.GetNode("ExposureTime"))

    if exposure == 'auto':
        exposure_auto.SetIntValue(exposure_auto.GetEntryByName("Continuous").GetValue())
        print("Exposure: Auto")
    else:
        exposure_auto.SetIntValue(exposure_auto.GetEntryByName("Off").GetValue())
        exposure = float(exposure)
        exposure = min(max(exposure, exposure_time.GetMin()), exposure_time.GetMax())
        exposure_time.SetValue(exposure)
        print(f"Exposure set to {exposure} µs")

    # Set gain
    gain_auto = PySpin.CEnumerationPtr(nodemap.GetNode("GainAuto"))
    gain_val = PySpin.CFloatPtr(nodemap.GetNode("Gain"))

    if gain == 'auto':
        gain_auto.SetIntValue(gain_auto.GetEntryByName("Continuous").GetValue())
        print("Gain: Auto")
    else:
        gain_auto.SetIntValue(gain_auto.GetEntryByName("Off").GetValue())
        gain = float(gain)
        gain = min(max(gain, gain_val.GetMin()), gain_val.GetMax())
        gain_val.SetValue(gain)
        print(f"Gain set to {gain} dB")

def acquire_images(mode='gray', exposure='auto', gain='auto'):
    system = PySpin.System.GetInstance()
    cam_list = system.GetCameras()

    if cam_list.GetSize() == 0:
        print("No camera detected.")
        cam_list.Clear()
        system.ReleaseInstance()
        return

    cam = cam_list.GetByIndex(0)
    cam.Init()

    # Set camera exposure, gain, and pixel format
    set_camera_settings(cam, exposure, gain)

    cam.BeginAcquisition()
    print("Acquisition started. Press 'q' to quit.")

    try:
        while True:
            image_result = cam.GetNextImage()

            if image_result.IsIncomplete():
                print("Image incomplete with status %d..." % image_result.GetImageStatus())
                image_result.Release()
                continue

            # Diagnostic output
            # print("Pixel format:", image_result.GetPixelFormatName())

            # Get image as NumPy array directly
            try:
                img = image_result.GetNDArray()
            except Exception as e:
                print("Failed to get NDArray:", e)
                image_result.Release()
                continue

            if mode == 'gray':
                display_img = img
            elif mode == 'heatmap':
                display_img = cv2.applyColorMap(img, cv2.COLORMAP_JET)
            else:
                print(f"Invalid mode: {mode}")
                break

            cv2.imshow('Live View - ' + mode, display_img)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

            image_result.Release()

    finally:
        cam.EndAcquisition()
        cam.DeInit()
        del cam
        cam_list.Clear()
        system.ReleaseInstance()
        cv2.destroyAllWindows()


def print_device_nodes(cam):
    nodemap_tldevice = cam.GetTLDeviceNodeMap()
    for node in nodemap_tldevice.GetNodes():
        print(node.GetName())


def print_camera_nodes(cam):
    nodemap = cam.GetNodeMap()
    print("=== Camera Main Node Map ===")
    for node in nodemap.GetNodes():
        print(node.GetName())

def print_float_nodes(cam):
    nodemap = cam.GetNodeMap()
    print("=== Float Nodes with values ===")
    for node in nodemap.GetNodes():
        try:
            float_node = PySpin.CFloatPtr(node)
            if PySpin.IsAvailable(float_node) and PySpin.IsReadable(float_node):
                print(f"{node.GetName()}: {float_node.GetValue()}")
        except Exception:
            # Not a float node
            pass

def get_camera_and_start(exposure='auto', gain='auto'):
    system = PySpin.System.GetInstance()
    cam_list = system.GetCameras()

    if cam_list.GetSize() == 0:
        print("No camera detected.")
        cam_list.Clear()
        system.ReleaseInstance()
        return None, None, None

    cam = cam_list.GetByIndex(0)
    cam.Init()

    # Print camera nodes here:
    # print_camera_nodes(cam)
    # print_float_nodes(cam)

    set_camera_settings(cam, exposure, gain)
    cam.BeginAcquisition()
    return cam, cam_list, system


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Live camera viewer using PySpin.")
    parser.add_argument('--mode', choices=['gray', 'heatmap'], default='gray', help='Display mode: gray or heatmap')
    parser.add_argument('--exposure', default='auto', help='Exposure time in µs or \"auto\"')
    parser.add_argument('--gain', default='auto', help='Gain in dB or \"auto\"')

    args = parser.parse_args()

    acquire_images(mode=args.mode, exposure=args.exposure, gain=args.gain)
