desktop_conf = configuration_data()
desktop_conf.set('bindir', join_paths(get_option('prefix'), get_option('bindir')))
desktop_conf.set('VERSION', meson.project_version())

desktop_in = configure_file(
  input: 'com.aymanbagabas.Glyrics.desktop.in.in',
  output: 'com.aymanbagabas.Glyrics.desktop.in',
  configuration: desktop_conf
)

desktop_file = i18n.merge_file(
  input: desktop_in,
  output: 'com.aymanbagabas.Glyrics.desktop',
  type: 'desktop',
  po_dir: '../po',
  install: true,
  install_dir: join_paths(get_option('datadir'), 'applications')
)

desktop_utils = find_program('desktop-file-validate', required: false)
if desktop_utils.found()
  test('Validate desktop file', desktop_utils,
    args: [desktop_file]
  )
endif

appstream_file = i18n.merge_file(
  input: 'com.aymanbagabas.Glyrics.appdata.xml.in',
  output: 'com.aymanbagabas.Glyrics.appdata.xml',
  po_dir: '../po',
  install: true,
  install_dir: join_paths(get_option('datadir'), 'appdata')
)

appstream_util = find_program('appstream-util', required: false)
if appstream_util.found()
  test('Validate appstream file', appstream_util,
    args: ['validate', appstream_file]
  )
endif

install_data('com.aymanbagabas.Glyrics.gschema.xml',
  install_dir: join_paths(get_option('datadir'), 'glib-2.0/schemas')
)

compile_schemas = find_program('glib-compile-schemas', required: false)
if compile_schemas.found()
  test('Validate schema file', compile_schemas,
    args: ['--strict', '--dry-run', meson.current_source_dir()]
  )
endif
