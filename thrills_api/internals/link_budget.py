import numpy as np
from thrills_api.internals.gas_model import gasModel

# From "Updated MCS_RCPI_Range.xlsx"
# Originally from https://bluwireless.atlassian.net/servicedesk/customer/portal/2/CP-409
# Tweaked to get monotonic increase to make plots look nicer

# Add a derating factor.  This is here to approximate the mesh and VXLAN overhead.
# To be used until we get real numbers for mesh.
# 9/05/2023 Real numbers from BWT have been added below, derating changed back to 1x.
# https://bluwireless.atlassian.net/servicedesk/customer/portal/2/CP-565
# Numbers are measured in quarter and extrapolated to other bands.  SNR numbers are still from CP-409.
DERATING_FACTOR = 1

MCS_TABLE = {
    "SIXTEENTH": [
        {"SNR": None, "DATA_RATE": 0},
        {"SNR": 1, "DATA_RATE": 46 / 4},
        {"SNR": 2, "DATA_RATE": 121 / 4},
        {"SNR": 2.6, "DATA_RATE": 126 / 4},
        {"SNR": 3.2, "DATA_RATE": 148 / 4},
        {"SNR": 3.5, "DATA_RATE": 162 / 4},
        {"SNR": 4.5, "DATA_RATE": 194 / 4},
        {"SNR": 6, "DATA_RATE": 240 / 4},
        {"SNR": 7.3, "DATA_RATE": 285 / 4},
        {"SNR": 8, "DATA_RATE": 305 / 4},
        {"SNR": 10, "DATA_RATE": 376 / 4},
        {"SNR": 12, "DATA_RATE": 458 / 4},
        {"SNR": 14, "DATA_RATE": 530 / 4},
    ],
    "EIGHTH": [
        {"SNR": None, "DATA_RATE": 0 / 2},
        {"SNR": 1, "DATA_RATE": 46 / 2},
        {"SNR": 2, "DATA_RATE": 121 / 2},
        {"SNR": 2.6, "DATA_RATE": 126 / 2},
        {"SNR": 3.2, "DATA_RATE": 148 / 2},
        {"SNR": 3.5, "DATA_RATE": 162 / 2},
        {"SNR": 4.5, "DATA_RATE": 194 / 2},
        {"SNR": 6, "DATA_RATE": 240 / 2},
        {"SNR": 7.3, "DATA_RATE": 285 / 2},
        {"SNR": 8, "DATA_RATE": 305 / 2},
        {"SNR": 10, "DATA_RATE": 376 / 2},
        {"SNR": 12, "DATA_RATE": 458 / 2},
        {"SNR": 14, "DATA_RATE": 530 / 2},
    ],
    "QUARTER": [
        {"SNR": None, "DATA_RATE": 0},
        {"SNR": 1, "DATA_RATE": 46},
        {"SNR": 2, "DATA_RATE": 121},
        {"SNR": 2.6, "DATA_RATE": 126},
        {"SNR": 3.2, "DATA_RATE": 148},
        {"SNR": 3.5, "DATA_RATE": 162},
        {"SNR": 4.5, "DATA_RATE": 194},
        {"SNR": 6, "DATA_RATE": 240},
        {"SNR": 7.3, "DATA_RATE": 285},
        {"SNR": 8, "DATA_RATE": 305},
        {"SNR": 10, "DATA_RATE": 376},
        {"SNR": 12, "DATA_RATE": 458},
        {"SNR": 14, "DATA_RATE": 530},
    ],
    "HALF": [
        {"SNR": None, "DATA_RATE": 0},
        {"SNR": 1, "DATA_RATE": 46 * 2},
        {"SNR": 2.5, "DATA_RATE": 121 * 2},
        {"SNR": 3.2, "DATA_RATE": 126 * 2},
        {"SNR": 3.8, "DATA_RATE": 148 * 2},
        {"SNR": 4.3, "DATA_RATE": 162 * 2},
        {"SNR": 5.6, "DATA_RATE": 194 * 2},
        {"SNR": 7, "DATA_RATE": 240 * 2},
        {"SNR": 8.4, "DATA_RATE": 285 * 2},
        {"SNR": 9, "DATA_RATE": 305 * 2},
        {"SNR": 11, "DATA_RATE": 376 * 2},
        {"SNR": 13, "DATA_RATE": 458 * 2},
        {"SNR": 14, "DATA_RATE": 530 * 2},
    ],
    "FULL": [
        {"SNR": None, "DATA_RATE": 0},
        {"SNR": 1, "DATA_RATE": 46 * 4},
        {"SNR": 2.6, "DATA_RATE": 121 * 4},
        {"SNR": 3.2, "DATA_RATE": 126 * 4},
        {"SNR": 3.7, "DATA_RATE": 148 * 4},
        {"SNR": 4.4, "DATA_RATE": 162 * 4},
        {"SNR": 5.4, "DATA_RATE": 194 * 4},
        {"SNR": 7, "DATA_RATE": 240 * 4},
        {"SNR": 8.5, "DATA_RATE": 285 * 4},
        {"SNR": 9.7, "DATA_RATE": 305 * 4},
        {"SNR": 13, "DATA_RATE": 376 * 4},
        {"SNR": 18.5, "DATA_RATE": 458 * 4},
        {"SNR": 21, "DATA_RATE": 530 * 4},
    ],
}

# TODO pull from the same source as the dropdown labels.
POWER_TABLE = [44, 40, 36, 32]


def LinkRange(RxGain_dB, Freq_GHz, Mcs=1, Altitude_ft=0, ScanLoss=0, Power=44, ChannelWidth="FULL"):
    # Constants
    # NoiseFigureBaseline = 5  # The noise figure used to calculate the required RX power
    # NoiseFigureBaseline: 7.5

    # Note: No RX constants, because the NF calculation is nontrivial
    # I used modified required RX power levels instead.

    ChannelScaler = {
        "FULL": 1,
        "HALF": 0.5,
        "QUARTER": 0.25,
        "EIGHTH": 0.125,
        "SIXTEENTH": 0.0625,
    }

    Altitude_km = 0.0003048 * Altitude_ft

    BW_MHz = 1800 * ChannelScaler[ChannelWidth]
    PA_Backoff = 0

    # Receiver #
    Kb = 1.38064852e-23
    T_C = 20  #
    T_K = T_C + 273
    Noise_dBW = 10 * np.log10(Kb * T_K * BW_MHz * 1e6)  # dBW

    Rx_NF = 7
    Rx_Loss = 1
    Rx_Sensitivity_dBm = Noise_dBW + 30 + Rx_NF + Rx_Loss

    Rx_AntennaGain = RxGain_dB - np.abs(ScanLoss)

    Rx_SensitivityAntenna_dBmi = Rx_Sensitivity_dBm - Rx_AntennaGain
    Rx_PowerRequiredAntenna_dBmi = Rx_SensitivityAntenna_dBmi + MCS_TABLE[ChannelWidth][Mcs]["SNR"]

    # Transmitter
    EIRP_dBm = Power - PA_Backoff - np.abs(ScanLoss)

    LossPerkm = gasModel(Freq_GHz, alt_km=Altitude_km)  # Add in the path loss to the required power

    # Pr = Pt + G1 + G2 + 20*np.log10(lam/(4*pi*d))
    AllowedPathLoss_dB = (
        Rx_PowerRequiredAntenna_dBmi - EIRP_dBm
    )  # Actually a path "gain" because it's negative.  Used for range calculation

    # Wavelength
    c = 299792  # km/sec
    f_Hz = Freq_GHz * 1e9
    lam_km = c / f_Hz

    d_km = find_range(AllowedPathLoss_dB, LossPerkm, lam_km)

    # Apply max MCS of 10 (TBR) to Auto 0
    MaxMCS = 10
    if Power > 41 and Mcs > MaxMCS:
        Mcs = MaxMCS
    DataRate_Mbps = MCS_TABLE[ChannelWidth][Mcs]["DATA_RATE"] * DERATING_FACTOR

    # Covertness range
    # Definition of covert:
    # Received power density should be 10dB below noise floor (-90dBm/Hz) at 2km

    # Pr = Noise - 10
    # # Note: We only include the Tx antenna gain here to keep it general.  So this basically assumes
    # # the eavesdropping antenna is isotropic.
    # X = Pr - Pt - G1  # - G2 # Used for range calculation
    # d_covert_km = find_range(X, LossPerkm, lam_km)

    return (d_km, LossPerkm, DataRate_Mbps)


def find_range(AllowedPathLoss_dB, LossPerkm, lam):
    min_step_km = 0.001
    num_pts = 101

    dv = np.arange(min_step_km, min_step_km * num_pts, min_step_km)  # km

    # Approximate solution to:
    # Pr = Pt + G1 + G2 + 20*np.log10(lam/(4*pi*d)) - Loss*d
    # With the substitution X = Pr - Pt - G1 - G2
    # X = 20*np.log10(lam/(4*pi*d)) - Loss*d

    X0 = 20 * np.log10(lam / (4 * np.pi * dv)) - LossPerkm * dv - AllowedPathLoss_dB
    # print(X)

    if max(X0) < 0:  # Unable to close link at any range
        distance = 0
    else:
        while min(X0) > 0:  # Scale up the distance range until we find the crossover
            dv = dv * (num_pts - 1)
            X0 = 20 * np.log10(lam / (4 * np.pi * dv)) - LossPerkm * dv - AllowedPathLoss_dB

        # X0 = 20*np.log10(lam/(4*np.pi*dv)) - LossPerkm*dv - X
        # Find where X0 = 0

        distance = findZero(X0, dv)

    # print(d_interp(0))
    return distance


def findZero(XX, YY):
    zc = np.where(np.diff(np.sign(XX)))[0][0]  # Find the index just before the zero crossing
    x = [XX[zc], XX[zc + 1]]
    y = [YY[zc], YY[zc + 1]]
    yZero = y[0] + (0 - x[0]) * (y[1] - y[0]) / (x[1] - x[0])
    return yZero


m_RxGain_dB = 18 + 1  # Using 18dB, the link budget is consistently more pessimistic than measured results


def getLinkBudget(Freq_GHz, Alt, Power, ChannelWidth):
    Mcs_v = np.arange(1, 13, dtype="int")  # Modulation

    Range_km_v = np.zeros_like(Mcs_v, dtype="float")
    DataRate_Mbps_v = np.zeros_like(Mcs_v, dtype="float")

    for dd in range(len(Mcs_v)):
        (Range_km_v[dd], loss_per_km, DataRate_Mbps_v[dd]) = LinkRange(
            RxGain_dB=m_RxGain_dB,
            Freq_GHz=Freq_GHz,
            Mcs=Mcs_v[dd],
            Altitude_ft=Alt,
            Power=Power,
            ChannelWidth=ChannelWidth,  # 1 = full, 1/4 = quarter, etc
        )

    return (Range_km_v, loss_per_km, DataRate_Mbps_v)
