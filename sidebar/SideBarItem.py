# coding=utf8
import sublime
import os
import re
import shutil

from .SideBarProject import SideBarProject

class Object():
	pass

def expandVars(path):
	for k, v in list(os.environ.items()):
		path = path.replace('%'+k+'%', v).replace('%'+k.lower()+'%', v)
	return path

class SideBarItem:

	def __init__(self, path, is_directory):
		self._path = path
		self._is_directory = is_directory

	def path(self, path = ''):
		if path == '':
			return self._path
		else:
			self._path = path
			self._is_directory = os.path.isdir(path)
			return path

	def pathWithoutProject(self):
		path = self.path()
		for directory in SideBarProject().getDirectories():
			path = path.replace(directory, '', 1)
		return path.replace('\\', '/')

	def pathProject(self):
		path = self.path()
		for directory in SideBarProject().getDirectories():
			path2 = path.replace(directory, '', 1)
			if path2 != path:
				return directory
		return False

	def projectURL(self, type):
		filename = os.path.dirname(sublime.packages_path())+'/Settings/SideBarEnhancements.json'
		if os.path.lexists(filename):
			#try:
				import json
				data = open(filename, 'r').read()
				data = data.replace('\t', ' ').replace('\\', '/').replace('\\', '/').replace('//', '/').replace('//', '/').replace('http:/', 'http://').replace('https:/', 'https://')
				data = json.loads(data, strict=False)

				for path in list(data.keys()):
					path2 = expandVars(path)
					#print('-------------------------------------------------------')
					#print('searching:')
					path2 = path2.replace('\\', '/').replace('\\', '/').replace('//', '/').replace('//', '/')
					#print(path2)
					#print('in:')
					path3 = self.path().replace('\\', '/').replace('\\', '/').replace('//', '/').replace('//', '/')
					#print(path3)
					#print('-------------------------------------------------------')
					path4 = re.sub(re.compile("^"+re.escape(path2), re.IGNORECASE), '', path3);
					#print(path4)
					if path4 != path3:
						url = data[path][type]
						if url:
							if url[-1:] != '/':
								url = url+'/'
						import urllib.request, urllib.parse, urllib.error
						return url+(re.sub("^/", '', urllib.parse.quote(path4)));

			#except:
			#	return False
		else:
			return False

	def isUnderCurrentProject(self):
		path = self.path()
		path2 = self.path()
		for directory in SideBarProject().getDirectories():
			path2 = path2.replace(directory, '', 1)
		return path != path2

	def pathRelativeFromProject(self):
		return re.sub('^/+', '', self.pathWithoutProject())

	def pathRelativeFromProjectEncoded(self):
		import urllib.request, urllib.parse, urllib.error
		return urllib.parse.quote(self.pathRelativeFromProject())

	def pathRelativeFromView(self):
		return os.path.relpath(self.path(), os.path.dirname(sublime.active_window().active_view().file_name())).replace('\\', '/')

	def pathRelativeFromViewEncoded(self):
		import urllib.request, urllib.parse, urllib.error
		return urllib.parse.quote(os.path.relpath(self.path(), os.path.dirname(sublime.active_window().active_view().file_name())).replace('\\', '/'))

	def pathAbsoluteFromProject(self):
		return self.pathWithoutProject()

	def pathAbsoluteFromProjectEncoded(self):
		import urllib.request, urllib.parse, urllib.error
		return urllib.parse.quote(self.pathAbsoluteFromProject())

	def uri(self):
		import urllib.request, urllib.parse, urllib.error
		return 'file:'+urllib.request.pathname2url(self.path());

	def join(self, name):
		return os.path.join(self.path(), name)

	def dirname(self):
		branch, leaf = os.path.split(self.path())
		return branch;

	def forCwdSystemPath(self):
		if self.isDirectory():
			return self.path()
		else:
			return self.dirname()

	def forCwdSystemName(self):
		if self.isDirectory():
			return '.'
		else:
			path = self.path()
			branch = self.dirname()
			leaf = path.replace(branch, '', 1).replace('\\', '').replace('/', '')
			return leaf

	def forCwdSystemPathRelativeFrom(self, relativeFrom):
		relative = SideBarItem(relativeFrom, os.path.isdir(relativeFrom))
		path = self.path().replace(relative.path(), '', 1).replace('\\', '/')
		if path == '':
			return '.'
		else:
			return re.sub('^/+', '', path)

	def forCwdSystemPathRelativeFromRecursive(self, relativeFrom):
		relative = SideBarItem(relativeFrom, os.path.isdir(relativeFrom))
		path = self.path().replace(relative.path(), '', 1).replace('\\', '/')
		if path == '':
			return '.'
		else:
			if self.isDirectory():
				return re.sub('^/+', '', path)+'/'
			else:
				return re.sub('^/+', '', path)

	def dirnameCreate(self):
		try:
			os.makedirs(self.dirname())
		except:
			pass

	def name(self):
		branch, leaf = os.path.split(self.path())
		return leaf;

	def nameEncoded(self):
		import urllib.request, urllib.parse, urllib.error
		return urllib.parse.quote(self.name());

	def namePretty(self):
		return self.name().replace(self.extension(), '').replace('-', ' ').replace('_', ' ').strip();

	def open(self):
		if sublime.platform() == 'osx':
			import subprocess
			subprocess.Popen(['open', self.name()], cwd=self.dirname())
		elif sublime.platform() == 'windows':
			import subprocess
			subprocess.Popen([self.name()], cwd=self.dirname(), shell=True)
		else:
			from . import desktop
			desktop.open(self.path())

	def edit(self):
		return sublime.active_window().open_file(self.path())

	def isDirectory(self):
		return self._is_directory

	def isFile(self):
		return self.isDirectory() == False

	def contentUTF8(self):
		import codecs
		return codecs.open(self.path(), 'r', 'utf-8').read()

	def contentBinary(self):
		return open(self.path(), "rb").read()

	def contentBase64(self):
		import base64
		base64text = base64.b64encode(self.contentBinary()).decode('utf-8')
		return 'data:'+self.mime()+';base64,'+(base64text.replace('\n', ''))

	def reveal(self):
		sublime.active_window().run_command("open_dir", {"dir": self.dirname(), "file": self.name()} )

	def write(self, content):
		open(self.path(), 'w+').write(content)

	def mime(self):
		import mimetypes
		return mimetypes.guess_type(self.path())[0] or 'application/octet-stream'

	def extension(self):
		return os.path.splitext('name'+self.name())[1].lower()

	def exists(self):
		return os.path.isdir(self.path()) or os.path.isfile(self.path())

	def create(self):
		if self.isDirectory():
			self.dirnameCreate()
			os.makedirs(self.path())
		else:
			self.dirnameCreate()
			self.write('')

	def copy(self, location, replace = False):
		location = SideBarItem(location, os.path.isdir(location));
		if location.exists() and replace == False:
			return False
		elif location.exists() and location.isFile():
			os.remove(location.path())

		location.dirnameCreate();
		if self.isDirectory():
			if location.exists():
				self.copyRecursive(self.path(), location.path())
			else:
				shutil.copytree(self.path(), location.path())
		else:
			shutil.copy2(self.path(), location.path())
		return True

	def copyRecursive(self, _from, _to):

		if os.path.isfile(_from) or os.path.islink(_from):
			try:
				os.makedirs(os.path.dirname(_to));
			except:
				pass
			if os.path.exists(_to):
				os.remove(_to)
			shutil.copy2(_from, _to)
		else:
			try:
				os.makedirs(_to);
			except:
				pass
			for content in os.listdir(_from):
				__from = os.path.join(_from, content)
				__to = os.path.join(_to, content)
				self.copyRecursive(__from, __to)

	def move(self, location, replace = False):
		location = SideBarItem(location, os.path.isdir(location));
		if location.exists() and replace == False:
			if self.path().lower() == location.path().lower():
				pass
			else:
				return False
		elif location.exists() and location.isFile():
			os.remove(location.path())

		if self.path().lower() == location.path().lower():
			location.dirnameCreate();
			os.rename(self.path(), location.path()+'.sublime-temp')
			os.rename(location.path()+'.sublime-temp', location.path())
			self._moveMoveViews(self.path(), location.path())
		else:
			location.dirnameCreate();
			if location.exists():
				self.moveRecursive(self.path(), location.path())
			else:
				os.rename(self.path(), location.path())
			self._moveMoveViews(self.path(), location.path())
		return True

	def moveRecursive(self, _from, _to):
		if os.path.isfile(_from) or os.path.islink(_from):
			try:
				os.makedirs(os.path.dirname(_to));
			except:
				pass
			if os.path.exists(_to):
				os.remove(_to)
			os.rename(_from, _to)
		else:
			try:
				os.makedirs(_to);
			except:
				pass
			for content in os.listdir(_from):
				__from = os.path.join(_from, content)
				__to = os.path.join(_to, content)
				self.moveRecursive(__from, __to)
			os.rmdir(_from)

	def _moveMoveViews(self, old, location):
		for window in sublime.windows():
			active_view = window.active_view()
			views = []
			for view in window.views():
				if view.file_name():
					views.append(view)
			views.reverse();
			for view in views:
				if old == view.file_name():
					active_view = self._moveMoveView(window, view, location, active_view)
				elif view.file_name().find(old+'\\') == 0:
					active_view = self._moveMoveView(window, view, view.file_name().replace(old+'\\', location+'\\', 1), active_view)
				elif view.file_name().find(old+'/') == 0:
					active_view = self._moveMoveView(window, view, view.file_name().replace(old+'/', location+'/', 1), active_view)

	def _moveMoveView(self, window, view, location, active_view):
		if active_view == view:
			is_active_view = True
		else:
			is_active_view = False

		options = Object()

		options.scroll = view.viewport_position()

		options.selections = [[item.a, item.b] for item in view.sel()]

		options.marks = [[item.a, item.b] for item in view.get_regions("mark")]

		options.bookmarks = [[item.a, item.b] for item in view.get_regions("bookmarks")]

		if int(sublime.version()) >= 2167:
			options.folds = [[item.a, item.b] for item in view.folded_regions()]
		else:
			options.folds = [[item.a, item.b] for item in view.unfold(sublime.Region(0, view.size()))]

		options.syntax = view.settings().get('syntax')

		try:
			_window = window or view.window() or sublime.active_window()
			options.position = _window.get_view_index(view)
		except:
			options.position = False

		window.focus_view(view)
		if view.is_dirty():
			options.content = view.substr(sublime.Region(0, view.size()))
			view.window().run_command('revert')
		else:
			options.content = False

		_view = view
		view = window.open_file(location)
		window.focus_view(_view)
		window.run_command('close')

		sublime.set_timeout(lambda: self._moveRestoreView(view, options, window), 200)

		if is_active_view:
			window.focus_view(view)
			return view
		else:
			window.focus_view(active_view)
			return active_view

	def _moveRestoreView(self, view, options, window):
		if view.is_loading():
			sublime.set_timeout(lambda: self._moveRestoreView(view, options, window), 100)
		else:
			if options.content != False:
				edit = view.begin_edit()
				view.replace(edit, sublime.Region(0, view.size()), options.content);
				view.sel().clear()
				view.sel().add(sublime.Region(0))
				view.end_edit(edit)

			if options.position != False:
				try:
					_window = window or view.window() or sublime.active_window()
					group, index = options.position
					_window.set_view_index(view, group, index)
				except:
					pass

			if options.syntax:
				view.settings().set('syntax', options.syntax);

			for r in options.folds:
				view.fold(sublime.Region(r[0], r[1]))

			view.sel().clear()
			for r in options.selections:
				view.sel().add(sublime.Region(r[0], r[1]))

			rs = []
			for r in options.marks:
				rs.append(sublime.Region(r[0], r[1]))
			if len(rs):
				view.add_regions("mark", rs, "mark", "dot", sublime.HIDDEN | sublime.PERSISTENT)

			rs = []
			for r in options.bookmarks:
				rs.append(sublime.Region(r[0], r[1]))
			if len(rs):
				view.add_regions("bookmarks", rs, "bookmarks", "bookmark", sublime.HIDDEN | sublime.PERSISTENT)

			view.set_viewport_position(options.scroll, False)

	def closeViews(self):
		path = self.path()
		closed_items = []
		for window in sublime.windows():
			active_view = window.active_view()
			views = []
			for view in window.views():
				if view.file_name():
					views.append(view)
			views.reverse();
			for view in views:
				if path == view.file_name():
					if view.window():
						closed_items.append([view.file_name(), view.window(), view.window().get_view_index(view)])
					if len(window.views()) == 1:
						window.new_file()
					window.focus_view(view)
					window.run_command('revert')
					window.run_command('close')
				elif view.file_name().find(path+'\\') == 0:
					if view.window():
						closed_items.append([view.file_name(), view.window(), view.window().get_view_index(view)])
					if len(window.views()) == 1:
						window.new_file()
					window.focus_view(view)
					window.run_command('revert')
					window.run_command('close')
				elif view.file_name().find(path+'/') == 0:
					if view.window():
						closed_items.append([view.file_name(), view.window(), view.window().get_view_index(view)])
					if len(window.views()) == 1:
						window.new_file()
					window.focus_view(view)
					window.run_command('revert')
					window.run_command('close')

			# try to repaint
			try:
				window.focus_view(active_view)
				window.focus_view(window.active_view())
			except:
				try:
					window.focus_view(window.active_view())
				except:
					pass
		return closed_items
