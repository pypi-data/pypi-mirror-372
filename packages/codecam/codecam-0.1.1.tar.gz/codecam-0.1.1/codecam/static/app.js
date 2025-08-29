function browse() {
  const path = document.getElementById('path').value;
  fetch('/browse', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ path })
  })
  .then(r => r.json())
  .then(data => {
    const filesDiv = document.getElementById('files');
    filesDiv.innerHTML = '';

    if (data.files && Array.isArray(data.files)) {
      const fileTree = buildFileTree(data.files);
      filesDiv.appendChild(fileTree);
    } else {
      filesDiv.textContent = 'No files found or invalid path.';
    }
  });
}

function buildFileTree(files) {
  const fileTree = document.createElement('ul');
  fileTree.classList.add('tree');
  const fileMap = {};

  files.forEach(file => {
    const parts = file.split('/');
    let current = fileMap;
    parts.forEach((part, index) => {
      if (!current[part]) {
        current[part] = {
          children: {},
          isFile: index === parts.length - 1,
          fullPath: file
        };
      }
      current = current[part].children;
    });
  });

  function createTreeElement(node, path) {
    const li = document.createElement('li');

    const checkbox = document.createElement('input');
    checkbox.type = 'checkbox';
    checkbox.value = node.isFile ? node.fullPath : path;
    checkbox.checked = node.isFile && selectedFiles.includes(node.fullPath);

    // toggle all descendants if a directory checkbox is toggled
    checkbox.addEventListener('change', () => {
      if (!node.isFile) {
        checkAllInDirectory(path, checkbox.checked);
      }
    });

    const label = document.createElement('span');
    label.textContent = node.isFile
      ? node.fullPath
      : (path === '.' ? currentDirectory : path.split('/').pop());

    li.appendChild(checkbox);
    li.appendChild(document.createTextNode(' '));
    li.appendChild(label);

    const childrenKeys = Object.keys(node.children);
    if (childrenKeys.length > 0) {
      const ul = document.createElement('ul');
      ul.classList.add('tree');
      for (const key of childrenKeys) {
        const child = node.children[key];
        const childPath = path === '.' ? key : `${path}/${key}`;
        ul.appendChild(createTreeElement(child, childPath));
      }
      li.appendChild(ul);
    }

    return li;
  }

  const roots = Object.keys(fileMap);
  for (const key of roots) {
    fileTree.appendChild(createTreeElement(fileMap[key], key));
  }
  return fileTree;
}

function checkAllInDirectory(directory, check) {
  const boxes = document.querySelectorAll('#files input[type="checkbox"]');
  const dir = directory.replace(/^\.\//, '');
  boxes.forEach(cb => {
    const v = cb.value.replace(/^\.\//, '');
    if (v.startsWith(dir + '/') || v === dir) {
      cb.checked = check;
    }
  });
}

function checkAll() {
  const boxes = document.querySelectorAll('#files input[type="checkbox"]');
  boxes.forEach(cb => cb.checked = true);
}

function uncheckAll() {
  const boxes = document.querySelectorAll('#files input[type="checkbox"]');
  boxes.forEach(cb => cb.checked = false);
}

function generate() {
  const checkboxes = document.querySelectorAll('#files input[type="checkbox"]');
  const files = Array.from(checkboxes)
    .filter(cb => cb.checked && cb.value.includes('/'))
    .map(cb => cb.value);

  fetch('/generate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ files })
  })
  .then(r => r.json())
  .then(data => {
    document.getElementById('result').value = data.result || '';
  });
}

// shut down the server on tab close/navigation
function shutdownServer() {
  try {
    fetch('/shutdown', { method: 'POST', keepalive: true, mode: 'no-cors' });
  } catch (e) { /* ignore */ }
}

// pagehide is more reliable than unload
window.addEventListener('pagehide', (e) => {
  if (!e.persisted) shutdownServer();
});

document.addEventListener('visibilitychange', () => {
  if (document.visibilityState === 'hidden') shutdownServer();
});

window.onload = function () { browse(); };

