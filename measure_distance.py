import numpy as np


class KalmanFilter:
    def __init__(self, process_variance, measurement_variance, estimated_measurement_variance):
        self.process_variance = process_variance
        self.measurement_variance = measurement_variance
        self.estimated_measurement_variance = estimated_measurement_variance
        self.posteri_estimate = 0.0
        self.posteri_error_estimate = 1.0

    def update(self, measurement):
        # Prediction update
        priori_estimate = self.posteri_estimate
        priori_error_estimate = self.posteri_error_estimate + self.process_variance

        # Measurement update
        blending_factor = priori_error_estimate / (priori_error_estimate + self.measurement_variance)
        self.posteri_estimate = priori_estimate + blending_factor * (measurement - priori_estimate)
        self.posteri_error_estimate = (1 - blending_factor) * priori_error_estimate

        return self.posteri_estimate


def calculate_average_rssi(rssi_values):
    """ Calculate the average of RSSI values using Kalman filter. """
    kalman_filter = KalmanFilter(process_variance=1e-5, measurement_variance=1, estimated_measurement_variance=1e-5)
    filtered_rssi = [kalman_filter.update(rssi) for rssi in rssi_values]
    return np.mean(filtered_rssi)


def rssi_to_distance(rssi, tx_power=-59, n=2):
    """ Convert RSSI value to distance in meters. """
    return 10 ** ((tx_power - rssi) / (10 * n))


def main():
    # Sample list of RSSI values
    rssi_values = [-34, -44, -33, -31, -43, -44, -32, -38, -45, -44, -40, -33, -45, -43, -40, -54, -37, -32, -43, -38, -36, -41, -38, -32, -40, -39, -40, -49, -32, -37, -60, -50, -36, -35, -44, -33, -33, -34, -44, -37, -32, -33, -42, -31, -31, -32, -39, -32, -37, -38, -50, -39, -49, -39, -41, -46, -33, -33, -38, -43, -37, -42, -32, -34, -43, -32, -33, -33, -43, -33, -33, -44, -33, -36, -44, -33, -34, -34, -44, -33, -44, -44, -33, -37, -44, -44, -33, -70, -44, -33, -34, -43, -33, -34, -71, -33, -37, -43, -34, -43, -43, -33, -37, -44, -33, -33, -35, -42, -33, -37, -43, -33, -37, -35, -43, -33, -35, -43, -33, -35, -43, -33, -37, -43, -33, -37, -43, -33, -38, -43, -33, -38, -43, -34, -39, -39, -44, -34, -39, -44, -34, -39, -44, -36, -40, -44, -37, -37, -34, -40, -39, -45, -34, -39, -44, -34, -34, -40, -44, -36, -39, -39, -44, -37, -39, -45, -44, -36, -40, -44, -36, -39, -44, -44, -37, -40, -44, -34, -39, -44, -44, -34, -44, -34, -39, -45, -44, -33, -39, -45, -45, -34, -39, -44, -34, -40, -40, -46, -38, -41, -67, -39, -40, -47, -45, -46, -42, -52, -37, -36, -36, -41, -30, -33, -46, -40, -42, -50, -37, -37, -38, -52, -38, -38, -39, -45, -38, -37, -37, -43, -34, -44, -33, -33, -38, -44, -39, -40, -70, -37, -41, -49, -38, -42, -51, -38, -41, -54, -38, -41, -41, -53, -37, -41, -40, -50, -34, -39, -39, -49, -33, -38, -38, -48, -33, -45, -32, -34, -33, -43, -32, -33, -33, -43, -37, -68, -36, -39, -39, -48, -39, -40, -52, -38, -39, -55, -38, -39, -39, -48, -39, -40, -49, -50, -40, -39, -49, -38, -38, -39, -45, -39, -40, -45, -44, -44, -71, -45, -48, -49, -49, -47, -42, -45, -48, -39, -38, -41, -49, -72, -39, -47, -34, -38, -37, -45, -33, -37, -37, -44, -33, -34, -44, -44, -33, -33, -44, -44, -34, -44, -33, -33, -34, -44, -33, -34, -34, -44, -33, -34, -34, -45, -33, -34, -34, -45, -33, -34]

    # Calculate average RSSI using Kalman filter
    average_rssi = calculate_average_rssi(rssi_values)
    print(f"Average RSSI: {average_rssi:.2f} dBm")

    # Estimate distance
    estimated_distance = rssi_to_distance(average_rssi, tx_power=-31, n=2.5)
    print(estimated_distance)


if __name__ == "__main__":
    main()
