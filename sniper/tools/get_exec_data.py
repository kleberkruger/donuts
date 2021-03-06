#!/usr/bin/env python

import sys, json, sniper_lib


def is_donuts(config):
  key = 'donuts/enabled'
  return config[key] if key in config else False

def is_picl(config):
  key = 'picl/enabled'
  return config[key] if key in config else False


def get_project_type(config):
  return 'donuts' if is_donuts(config) else 'picl' if is_picl(config) else 'baseline'


def get_runtime(res):
  results = res['results']
  config = res['config']
  ncores = int(config['general/total_cores'])
  
  if 'barrier.global_time_begin' in results:
    time0_begin = results['barrier.global_time_begin']
    time0_end = results['barrier.global_time_end']
  
  if 'barrier.global_time' in results:
    time0 = results['barrier.global_time'][0]
  else:
    time0 = time0_begin - time0_end

  results['performance_model.elapsed_time_fixed'] = [ time0 for c in range(ncores) ]
  results['performance_model.cycle_count_fixed'] = [
    results['performance_model.elapsed_time_fixed'][c] * results['fs_to_cycles_cores'][c]
    for c in range(ncores)
  ]
  return int(results['performance_model.cycle_count_fixed'][0])


def get_num_mem_access(res):
  results = res['results']
  return list(map(sum, list(zip(results['dram.reads'], results['dram.writes']))))[0]


def get_num_mem_writes(res):
  results = res['results']
  return results['dram.writes'][0]


def get_num_mem_logs(res):
  project_type = get_project_type(res['config'])
  if project_type == 'baseline':
    return 0
  
  mem_log_key = {
    'donuts': 'dram.logs',
    'picl': 'onchip_undo_buffer.log_writes',
  }
  key = mem_log_key[project_type]
  results = res['results']
  return results[key][0]


def get_num_buffer_overflow(res):
  project_type = get_project_type(res['config'])
  if project_type == 'baseline':
    return 0
  
  mem_log_key = {
    'donuts': 'dram.log_ends',
    'picl': 'onchip_undo_buffer.overflow',
  }
  key = mem_log_key[project_type]
  results = res['results']
  return results[key][0]


def get_num_checkpoints(res):
  project_type = get_project_type(res['config'])
  if project_type == 'baseline':
    return 0

  results = res['results']
  return results['epoch.system_eid'][0]


def get_avg_bandwidth_usage(res):
  results = res['results']

  if 'barrier.global_time_begin' in results:
    time0_begin = results['barrier.global_time_begin']
    time0_end = results['barrier.global_time_end']
  
  if 'barrier.global_time' in results:
    time0 = results['barrier.global_time'][0]
  else:
    time0 = time0_begin - time0_end

  return float([100 * r / time0 if time0 else float('inf') for r in results['dram-queue.total-time-used']][0])


def main():
  path = sys.argv[1]
  error = None
  try:
    res = sniper_lib.get_results(0, path, None)
  except Exception as e:
    sys.stderr.write('Exception: {}.\n'.format(str(e)))
    error = e
  finally:
    data = {
      'runtime': get_runtime(res) if not error else 0,
      'avg_bandwidth_usage': get_avg_bandwidth_usage(res) if not error else 0.0,
      'num_mem_access': get_num_mem_access(res) if not error else 0,
      'num_mem_writes': get_num_mem_writes(res) if not error else 0,
      'num_mem_logs': get_num_mem_logs(res) if not error else 0,
      'num_buffer_overflow': get_num_buffer_overflow(res) if not error else 0,
      'num_checkpoints': get_num_checkpoints(res) if not error else 0,
      'error': str(error) if error else None
    }
    # sys.stdout.write(json.dumps(data, sort_keys=True))
    print(json.dumps(data, sort_keys=True))


if __name__ == "__main__":
  main()
