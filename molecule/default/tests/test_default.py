import os
import pytest
import testinfra.utils.ansible_runner
from time import sleep

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')


@pytest.mark.skip(reason="needs to be reviewed")
def test_celery_task(host):
    with host.sudo():
        host.check_output(
            'rm -f /tmp/celery/output.txt /tmp/celery/log.out')

    taskid = host.check_output(
        '/opt/celery/venv/bin/python %s %s %s %s %s %s %s %s %s %s %s %s',
        '/opt/celery/worker/tasks.py',
        '--inputpath', '/tmp/celery/input.txt',
        '--outputpath', '/tmp/celery',
        '--out', '/tmp/celery/log.out',
        'busybox', '--',
        'sh', '-c',
        'md5sum /input > /output/output.txt && echo Done'
    )
    assert taskid

    # WARNING: If the network is particularly slow the download of busybox
    # may take too long
    for i in range(20):
        got_outputs = (host.file('/tmp/celery/log.out').exists and
                       host.file('/tmp/celery/output.txt').exists)
        # Sleep first to allow time for writing
        sleep(10)
        if got_outputs:
            break

    flog = host.file('/tmp/celery/log.out')
    assert flog.exists
    assert flog.content_string.strip() == 'Done'

    fout = host.file('/tmp/celery/output.txt')
    assert fout.exists
    assert fout.content_string.strip() == \
        '5eb63bbbe01eeed093cb22bb8f5acdc3  /input'
