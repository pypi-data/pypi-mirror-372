STUB_DATA_FILE_MAPPING: dict[str, list[str]] = {
    # Experiments
    "chi01_scan": ["QM/Tuna-5/chi01_scan.json"],
    "coherence_t1": ["QM/Tuna-5/coherence_t1.json"],
    "coherence_t2": ["QM/Tuna-5/coherence_t2.json"],
    "readout_classifier_calibration": ["QM/Tuna-5/readout_classifier_calibration.json"],
    "resonator_spectroscopy": ["QM/Tuna-5/resonator_spectroscopy.json"],
    "resonator_spectroscopy_by_power": ["QM/Tuna-5/resonator_spectroscopy_by_power.json"],
    "resonator_spectroscopy_by_bias": ["QM/Tuna-5/resonator_spectroscopy_by_bias.json"],
    "ramsey": ["QM/Tuna-5/ramsey.json"],
    "power_rabi": ["QM/Tuna-5/power_rabi.json"],
    "transmon_anharmonicity": ["QM/Tuna-5/transmon_anharmonicity.json"],
    "transmon_spectroscopy": ["QM/Tuna-5/transmon_spectroscopy.json"],
    # Routines
    "feedline_discovery": [f"QM/Tuna-5/feedline_discovery/{n}.json" for n in range(1, 7)],
    "resonator_mapping": [f"QM/Tuna-5/resonator_mapping/{n}.json" for n in range(1, 17)],
    "transmon_discovery": [f"QM/Tuna-5/transmon_discovery/{n}.json" for n in range(1, 8)],
}
