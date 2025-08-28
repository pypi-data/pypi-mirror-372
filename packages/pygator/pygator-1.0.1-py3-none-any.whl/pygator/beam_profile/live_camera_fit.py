import cv2
from fit_gaussian import *
from live_camera import get_camera_and_start
import argparse

def draw_fit_info(image, params, color=(255,)):
    A, x0, y0, sigma_x, sigma_y, B = params
    lines = [
        f"A      = {A:.1f}",
        f"x0     = {x0:.1f} pixels",
        f"y0     = {y0:.1f} pixels",
        f"sigma_x= {sigma_x:.1f} pixels",
        f"sigma_y= {sigma_y:.1f} pixels",
        f"B      = {B:.1f}"
    ]
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.5
    thickness = 1
    x, y = 10, 20
    for i, line in enumerate(lines):
        cv2.putText(image, line, (x, y + i * 20), font, font_scale, color, thickness)

def run_live_fit(mode='gray', exposure='auto', gain='auto', roi_size=300, downsample=2):
    cam, cam_list, system = get_camera_and_start(exposure, gain)
    if cam is None:
        return

    print("Live fitting started. Press 'q' to quit.")

    try:
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
                # params = fit_gaussian(img)
                # Meshgrid cache can be reused across frames
                if 'meshgrid_cache' not in locals():
                    meshgrid_cache = {}

                params = fit_gaussian_roi(img, roi_size=roi_size, downsample=downsample, meshgrid_cache=meshgrid_cache)

                # Draw ROI square
                half = roi_size // 2
                x0, y0 = int(params[1]), int(params[2])
                top_left = (max(0, x0 - half), max(0, y0 - half))
                bottom_right = (min(img.shape[1], x0 + half), min(img.shape[0], y0 + half))

                # Choose text color based on mode
                text_color = (255, 255, 255) if mode == 'heatmap' else (255,)
                draw_fit_info(img, params, color=text_color)

                center = (int(params[1]), int(params[2]))
                axes = (int(params[3] * 2), int(params[4] * 2))
                cv2.ellipse(img, center, axes, 0, 0, 360, 255, 1)
            except Exception as e:
                print("Fit failed:", e)

            # Apply heatmap if requested
            if mode == 'heatmap':
                display_img = cv2.applyColorMap(img, cv2.COLORMAP_JET)
                cv2.rectangle(display_img, top_left, bottom_right, (255, 0, 0), 1)  # Blue for heatmap
            else:
                display_img = img
                cv2.rectangle(display_img, top_left, bottom_right, (200,), 1)  # Light gray for grayscale

            cv2.imshow('Live Gaussian Fit', display_img)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    finally:
        cam.EndAcquisition()
        cam.DeInit()
        del cam
        cam_list.Clear()
        system.ReleaseInstance()
        cv2.destroyAllWindows()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', choices=['gray', 'heatmap'], default='gray', help='Display mode: gray or heatmap')
    parser.add_argument('--exposure', default='auto', help='Exposure in µs')
    parser.add_argument('--gain', default='auto', help='Gain in dB')
    parser.add_argument('--roi-size', type=int, default=300, help='Size of the ROI in pixels (e.g. 100-300)')
    parser.add_argument('--downsample', type=int, default=2, help='Downsampling factor (e.g. 1, 2, 4)')


    args = parser.parse_args()
    run_live_fit(
        mode=args.mode,
        exposure=args.exposure,
        gain=args.gain,
        roi_size=args.roi_size,
        downsample=args.downsample
)
