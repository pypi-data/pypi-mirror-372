from shouldersurfscore.defined_experiments import built_labs


def test_initial_lab():
    password = "9163"
    observed = "9613"
    analysis = built_labs.InitialShoulderSurfScorePaperLab.run(password, observed)
    print()
    print(analysis)
    assert analysis.actual_password == password
    assert analysis.observed_password == observed
    assert analysis.password_index == 2
    assert analysis.password_index_percent and analysis.password_index_percent < 0.00001
    assert analysis.elapsed_time.total_seconds() == 0
    assert analysis.device_unlocked
