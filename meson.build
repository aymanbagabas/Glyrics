project('glyrics',         version: '0.2.0 (Baby Lavender)',
  meson_version: '>= 0.46.0',
)

i18n = import('i18n')


subdir('data')
subdir('src')
subdir('po')

meson.add_install_script('build-aux/meson/postinstall.py')
