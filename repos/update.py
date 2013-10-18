#!/usr/bin/env python

import os
import re
import urllib2
import json
import netrc, base64
from xml.etree import ElementTree

to_clean = ['remote', 'revision', 'groups', 'sync-c']

def iterparent(tree):
	for parent in tree.iter():
		for child in parent:
			yield parent, child

def exists_repo_in_tree(lm, repository):
	for child in lm.iter():
		if 'name' in child.keys():
			if child.attrib['name'].endswith(repository):
				return True
	return False

def exists_path_in_tree(lm, path):
	for child in lm.iter():
		if path in child.attrib:
			return True
	return False

def get_safe_attrib(elem, name):
	if name in elem.keys():
		return True, elem.attrib[name]
	return False, None

def indent(elem, level=0):
	i = "\n" + level*"  "
	if len(elem):
		if not elem.text or not elem.text.strip():
			elem.text = i + "  "
		if not elem.tail or not elem.tail.strip():
			elem.tail = i
		for elem in elem:
			indent(elem, level+1)
		if not elem.tail or not elem.tail.strip():
			elem.tail = i
	else:
		if level and (not elem.tail or not elem.tail.strip()):
			elem.tail = i

def clean_tree(lm):
	for parent, child in iterparent(lm):
		if child.tag != 'project' and child.tag != 'manifest':
			parent.remove(child)
			continue
		for clean in to_clean:
			if clean in child.keys():
				del child.attrib[clean]
		if child.attrib['path'].startswith('/'):
			child.attrib['path'] = re.sub('^/', '', child.attrib['path'])

def update_github(user, outfile, manifest_url):
	print("Updating %s" % outfile)

	try:
		authtuple = netrc.netrc().authenticators("api.github.com")

		if authtuple:
			githubauth = base64.encodestring('%s:%s' % (authtuple[0], authtuple[1])).replace('\n', '')
		else:
			githubauth = None
	except:
		githubauth = None

	if manifest_url != None:
		manifestreq = urllib2.Request(manifest_url, headers={"Accept": "application/xml"})
		lm = ElementTree.parse(urllib2.urlopen(manifestreq)).getroot()
	else:
		lm = ElementTree.Element("manifest")

	page = 1
	while True:
		githubreq = urllib2.Request("https://api.github.com/users/%s/repos?per_page=100&page=%d" % (user, page))
		if githubauth:
			githubreq.add_header("Authorization", "Basic %s" & githubauth)
		result = json.loads(urllib2.urlopen(githubreq).read())
		if len(result) == 0:
			break
		for repo in result:
			repo_name = repo['name']
			repo_target = repo['name'].replace("android", "").replace("platform", "").replace("_", "/")

			if exists_repo_in_tree(lm, repo_name):
				continue
			if exists_path_in_tree(lm, repo_target):
				continue

			project = ElementTree.Element("project", attrib = {"path": repo_target, "name": "%s/%s" % (user, repo_name)})
			lm.append(project)
		page = page + 1

	clean_tree(lm)

	indent(lm, 0)
	raw_xml = ElementTree.tostring(lm)
	raw_xml = '<?xml version="1.0" encoding="UTF-8"?>' + raw_xml

	print("Writing %s" % outfile)
	f = open(outfile, 'w')
	f.write(raw_xml)
	f.close()

def update_remote_manifests(repofile):
	print("Updating manifest files using %s" % repofile)

	remotetree = ElementTree.parse(repofile).getroot()

	for child in remotetree.iter():
		if child.tag != 'repo':
			continue

		remote_name = child.attrib['name']
		remote_url = child.attrib['url']

		has_manifest, manifest = get_safe_attrib(child, 'manifest')
		has_revision, revision = get_safe_attrib(child, 'revision')

		if 'github.com' in remote_url:
			user = remote_url.replace("https://github.com/", "")
			outfile = "%s.xml" % remote_name

			if has_manifest and has_revision:
				manifest_raw = "https://raw.github.com/%s/%s/%s/default.xml" % (user, manifest, revision)
			else:
				manifest_raw = None

			update_github(user, outfile, manifest_raw);

update_remote_manifests("../repos.xml")

