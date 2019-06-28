from unittest.mock import patch


def test_ping(swh_app, celery_session_worker):
    res = swh_app.send_task(
        'swh.lister.cgit.tasks.ping')
    assert res
    res.wait()
    assert res.successful()
    assert res.result == 'OK'


@patch('swh.lister.cgit.tasks.CGitLister')
def test_lister_no_url_prefix(lister, swh_app, celery_session_worker):
    # setup the mocked CGitLister
    lister.return_value = lister
    lister.run.return_value = None

    res = swh_app.send_task(
        'swh.lister.cgit.tasks.CGitListerTask',
        kwargs=dict(url='https://git.kernel.org/', instance='kernel'))
    assert res
    res.wait()
    assert res.successful()

    lister.assert_called_once_with(
           url='https://git.kernel.org/',
           url_prefix=None,
           instance='kernel')
    lister.db_last_index.assert_not_called()
    lister.run.assert_called_once_with()


@patch('swh.lister.cgit.tasks.CGitLister')
def test_lister_with_url_prefix(lister, swh_app, celery_session_worker):
    # setup the mocked CGitLister
    lister.return_value = lister
    lister.run.return_value = None

    res = swh_app.send_task(
        'swh.lister.cgit.tasks.CGitListerTask',
        kwargs=dict(url='https://cgit.kde.org/',
                    url_prefix='https://anongit.kde.org/', instance='kde'))
    assert res
    res.wait()
    assert res.successful()

    lister.assert_called_once_with(
           url='https://cgit.kde.org/',
           url_prefix='https://anongit.kde.org/',
           instance='kde')
    lister.db_last_index.assert_not_called()
    lister.run.assert_called_once_with()
