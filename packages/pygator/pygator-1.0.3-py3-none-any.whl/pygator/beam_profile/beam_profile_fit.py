import cv2
import numpy as np
import argparse
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import simpledialog, messagebox
from fit_gaussian import fit_gaussian_roi
from live_camera import get_camera_and_start
from pygator.module import fit_beam_profile_ODR
import csv

def draw_text(image, text, pos=(10, 20), color=(255,)):
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(image, text, pos, font, 0.5, color, 1)

def get_distance_input():
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    user_input = simpledialog.askstring("Distance Moved (inches)", 
                                        "Enter distance moved from previous position (inches, e.g. 1.0):")
    root.destroy()
    return user_input

def ask_to_save():
    root = tk.Tk()
    root.withdraw()
    response = messagebox.askyesno("Save Data", "Save recorded data to CSV?")
    root.destroy()
    return response

def beam_profile_fit(roi_size=300, downsample=2, exposure='auto', gain='auto',
                     pixel_size_um=6.9, output_file="beam_profile.csv", mode="gray"):

    # Convert pixel size to meters
    pixel_size_m = pixel_size_um * 1e-6

    cam, cam_list, system = get_camera_and_start(exposure, gain)
    if cam is None:
        return

    z_list = []
    wx_list = []
    wy_list = []
    wx_std_list = []
    wy_std_list = []

    # Temporary buffers for averaging
    wx_temp = []
    wy_temp = []

    meshgrid_cache = {}

    z_position = 0.0  # Initial z = 0 (meters)

    print("Live beam profiling started. Press:")
    print("  [r] Record current sample (adds to buffer)")
    print("  [R] Finalize buffer (mean/std saved to dataset)")
    print("  [n] Move camera (input distance in inches)")
    print("  [f] Fit data and finish")
    print("  [q] Quit without fitting")

    plt.ion()
    plt.figure("Beam Width Live Plot")

    try:
        recording = False  # add this at the top of your loop
        while True:
            image_result = cam.GetNextImage()
            if image_result.IsIncomplete():
                print("Incomplete image:", image_result.GetImageStatus())
                image_result.Release()
                continue

            try:
                img = image_result.GetNDArray().copy()
            except Exception as e:
                print("Error reading image:", e)
                image_result.Release()
                continue

            image_result.Release()

            try:
                params = fit_gaussian_roi(img, roi_size=roi_size, downsample=downsample, meshgrid_cache=meshgrid_cache)
                x0, y0 = int(params[1]), int(params[2])
                half = roi_size // 2
                top_left = (max(0, x0 - half), max(0, y0 - half))
                bottom_right = (min(img.shape[1], x0 + half), min(img.shape[0], y0 + half))
                cv2.rectangle(img, top_left, bottom_right, (255,), 1)

                sigma_x_px = params[3]
                sigma_y_px = params[4]

                # Convert to meters
                sigma_x_m = sigma_x_px * pixel_size_m
                sigma_y_m = sigma_y_px * pixel_size_m

                draw_text(img, f"sigma_x = {sigma_x_m*1e6:.2f} um", (10, 20))
                draw_text(img, f"sigma_y = {sigma_y_m*1e6:.2f} um", (10, 40))
                draw_text(img, f"z = {z_position*1000:.3f} mm", (10, 60))

                center = (x0, y0)
                axes = (int(params[3] * 2), int(params[4] * 2))
                cv2.ellipse(img, center, axes, 0, 0, 360, 255, 1)

            except Exception as e:
                print("Fit failed:", e)

            cv2.imshow('Beam Profile Fit', img)
            key = cv2.waitKey(1) & 0xFF

            # inside your while loop
            if key == ord('r'):  # Toggle recording on/off
                recording = not recording
                state = "ON" if recording else "OFF"
                print(f"Recording {state}...")

            # if recording is active, buffer every frame automatically
            if recording:
                wx_temp.append(sigma_x_m)
                wy_temp.append(sigma_y_m)
                print(f"Buffered sample: wx={sigma_x_m*1e6:.2f} um, wy={sigma_y_m*1e6:.2f} um")

            elif key == ord('R'):  # Finalize buffer
                if len(wx_temp) > 0:
                    sigma_x_mean = np.mean(wx_temp)
                    sigma_y_mean = np.mean(wy_temp)

                    # Compute std dev and enforce minimum uncertainty
                    sigma_x_std = max(np.std(wx_temp), 5e-6)
                    sigma_y_std = max(np.std(wy_temp), 5e-6)

                    wx_list.append(sigma_x_mean)
                    wy_list.append(sigma_y_mean)
                    wx_std_list.append(sigma_x_std)
                    wy_std_list.append(sigma_y_std)
                    z_list.append(z_position)

                    print(f"Recorded batch: z={z_position:.3f} m, "
                        f"wx={sigma_x_mean*1e6:.2f}±{sigma_x_std*1e6:.2f} um, "
                        f"wy={sigma_y_mean*1e6:.2f}±{sigma_y_std*1e6:.2f} um")

                    # Live plot
                    plt.clf()
                    plt.errorbar(z_list, np.array(wx_list)*1e6, yerr=np.array(wx_std_list)*1e6, fmt='o', label='wx', capsize=3)
                    plt.errorbar(z_list, np.array(wy_list)*1e6, yerr=np.array(wy_std_list)*1e6, fmt='o', label='wy', capsize=3)
                    plt.xlabel("z position [m]")
                    plt.ylabel("Beam width [um]")
                    plt.legend()
                    plt.title("Live Beam Width vs. z")
                    plt.tight_layout()
                    plt.draw()
                    plt.show(block=False)
                    plt.gcf().canvas.flush_events()
                    # Clear buffer for next z
                    wx_temp.clear()
                    wy_temp.clear()

            elif key == ord('n'):  # Move camera
                distance_str = get_distance_input()
                try:
                    dz_inch = float(distance_str)
                    dz_m = dz_inch * 0.0254  # inches → meters
                    z_position += dz_m
                    print(f"Moved by {dz_inch:.3f} in = {dz_m:.4f} m, new z = {z_position:.4f} m")
                except Exception:
                    print("Invalid distance.")

            elif key == ord('f'):  # Fit and save
                if len(z_list) < 3:
                    print("Not enough points to fit.")
                    continue

                print("Fitting...")
                z = np.array(z_list)
                wx = np.array(wx_list)
                wy = np.array(wy_list)
                wx_std = np.array(wx_std_list)
                wy_std = np.array(wy_std_list)

                sol_x, sol_y = fit_beam_profile_ODR(
                    z, wx, z, wy,
                    w0guess=300e-6,
                    z0guess=z_list[0],
                    zRguess=0.05,
                    wx_std=wx_std,
                    wy_std=wy_std,
                    z_std=0.005,
                    title='Beam Profile',
                    print_results=True,
                    frac_err=0.02
                )

                # Compute q-parameters
                q_x = f"{sol_x[1]:.4e} + i{sol_x[2]:.4e}"
                q_y = f"{sol_y[1]:.4e} + i{sol_y[2]:.4e}"
                print("q-parameter (x):", q_x)
                print("q-parameter (y):", q_y)

                # Annotate on the plot
                plt.gcf()  # get current figure
                plt.text(0.05, 0.95, f"q_x = {q_x}", transform=plt.gca().transAxes,
                        verticalalignment='top', fontsize=8, color='blue')
                plt.text(0.05, 0.90, f"q_y = {q_y}", transform=plt.gca().transAxes,
                        verticalalignment='top', fontsize=8, color='green')
                plt.draw()

                # Ask to save
                # Ask to save
                if ask_to_save():
                    with open(output_file, "w", newline="") as f:
                        writer = csv.writer(f)

                        # Main data header
                        writer.writerow(["z [m]", "wx [m]", "wy [m]", "wx_std [m]", "wy_std [m]"])

                        # Main data rows
                        for i in range(len(z_list)):
                            writer.writerow([z_list[i], wx_list[i], wy_list[i], wx_std_list[i], wy_std_list[i]])

                        # Blank line, then q-parameters
                        writer.writerow([])
                        writer.writerow(["q_x", f"'{q_x}'"])
                        writer.writerow(["q_y", f"'{q_y}'"])


                    print(f"Saved to {output_file}")

                break

            elif key == ord('q'):
                print("Quit without fitting.")
                break

    finally:
        cam.EndAcquisition()
        cam.DeInit()
        del cam
        cam_list.Clear()
        system.ReleaseInstance()
        cv2.destroyAllWindows()
        plt.ioff()
        plt.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Live Gaussian beam profiling with camera.\n\n"
                    "Example:\n"
                    "  python beam_profile.py --roi-size 400 --downsample 2 --exposure auto --gain auto --pixel-size 6.9 --output my_beam_scan.csv",
        formatter_class=argparse.RawTextHelpFormatter
        )
    parser.add_argument('--roi-size', type=int, default=300, help='ROI size in pixels')
    parser.add_argument('--downsample', type=int, default=2, help='Downsampling factor')
    parser.add_argument('--exposure', default='auto', help='Camera exposure (µs)')
    parser.add_argument('--gain', default='auto', help='Camera gain (dB)')
    parser.add_argument('--pixel-size', type=float, default=6.9, help='Pixel size in um (default 6.9)')
    parser.add_argument('--output', default="beam_profile.csv", help='Output CSV filename')
    parser.add_argument('--mode', choices=['gray', 'heatmap'], default='gray',
                    help='Display mode for live camera (default: gray)')
    args = parser.parse_args()

    beam_profile_fit(
        roi_size=args.roi_size,
        downsample=args.downsample,
        exposure=args.exposure,
        gain=args.gain,
        pixel_size_um=args.pixel_size,
        output_file=args.output
    )
