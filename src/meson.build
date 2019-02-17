pkgdatadir = join_paths(get_option('prefix'), get_option('datadir'), meson.project_name())
moduledir = join_paths(pkgdatadir, 'glyrics')
gnome = import('gnome')

inc_local = include_directories(get_option('prefix'))

gnome.compile_resources('glyrics',
  'glyrics.gresource.xml',
  gresource_bundle: true,
  install: true,
  install_dir: pkgdatadir,
)

python_name = 'python3'
python = import('python').find_installation(python_name)

conf = configuration_data()
conf.set('PYTHON', python_name)
conf.set('VERSION', meson.project_version())
conf.set('localedir', join_paths(get_option('prefix'), get_option('localedir')))
conf.set('pkgdatadir', pkgdatadir)

configure_file(
  input: 'glyrics.in',
  output: 'glyrics',
  configuration: conf,
  install: true,
  install_dir: get_option('bindir')
)

glyrics_sources = [
  '__init__.py',
  'gi_composites.py',
  'main.py',
  'window.py',
]

playerctl_dep = dependency('playerctl', required: true)
libglyr_dep = dependency('libglyr', required: true)
plyr_dep = python.dependency('plyr', required: true)

install_data(glyrics_sources, install_dir: moduledir)
