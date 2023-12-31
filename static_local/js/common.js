// メニューの表示ON/OFF
function menuControl() {
    // toggleボタン
    let sidemenuToggle = document.getElementById('toggle');
    // メインコンテンツを囲むmain要素
    let page = document.getElementById('sideMenu');

    // 表示状態 trueで表示中 falseで非表示
    let sidemenuStatus = true;
    // セッション情報のメニューステータスを取得
    let sidemenuStatusStr = window.sessionStorage.getItem(['sidemenuStatus']);
    // セットされていたらその値で更新
    if (sidemenuStatusStr) {
        if (sidemenuStatusStr == 'true') {
            sidemenuStatus = true;
        }
        else {
            sidemenuStatus = false;
            if (page.style.marginLeft == "") {
                page.style.cssText = 'margin-left: -270px';
            }
        }
    }

    // ボタンクリック時のイベント
    sidemenuToggle.addEventListener('click', () => {
        // 表示状態を判定
        if(sidemenuStatus){
            page.style.cssText = 'margin-left: -270px';
            sidemenuStatus = false;
        }
        else {
            page.style.cssText = 'margin-left: 0px';
            sidemenuStatus = true;
        }
        // ステータスをセッションへ書き出す
        window.sessionStorage.setItem(['sidemenuStatus'], [sidemenuStatus]);
    })
}

// セレクトボックスオプション更新
// pNendo：取得したいリストの年度
// url：Fetch先URL
// plistId：役職リストボックのID(#付き)
function renewSelectList(pNendo, url, pListId) {
    let lobj = document.querySelector(pListId);
    lobj.innerHTML = '';    // option全削除

    // CSRF対策
    const getCookie = (name) => {
        if (document.cookie && document.cookie !== '') {
            for (const cookie of document.cookie.split(';')) {
                const [key, value] = cookie.trim().split('=')
                if (key === name) {
                    return decodeURIComponent(value)
                }
            }
        }
    }
    const csrftoken = getCookie('csrftoken')

    // URLのクエリパラメータを管理
    const body = new URLSearchParams()
    body.append('nendo', pNendo)
    body.append('list_id', pListId)

    fetch(url, {
        method: 'POST',
        body: body,
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8',
          'X-CSRFToken': csrftoken,
        },
      })
        .then((response) => {
          // JSON形式に変換
          return response.json()
        })
        .then((data) => {
          // option追加
          let lid = data.list_id;
          let lobj = document.querySelector(lid);
          for (let i=0; i < data.rlist.length; i++) {
            let ldat = data.rlist.at(i);
            let opt = document.createElement("option");
            opt.value = ldat.at(0);
            opt.text = ldat.at(1);
            lobj.appendChild(opt);
          }
        })
        .catch((error) => {
          console.log(error)
          alert('fetch エラーが発生しました。')
        })
}

// ログアウト、パスワード変更のドロップダウンリスト
function dropDownList() {
    document.addEventListener('DOMContentLoaded', function() {
        var dropdowns = document.querySelectorAll('.js-dropdown');
        var DURATION = 200; // アニメーションの速さ
    
        function fadeOutMenu() {
            dropdowns.forEach(function(dropdown) {
                dropdown.classList.remove('is-active');
                var menu = dropdown.nextElementSibling;
                if (menu && menu.classList.contains('js-dropdown-menu')) {
                    menu.style.display = 'none';
                }
            });
        }
    
        dropdowns.forEach(function(dropdown) {
            dropdown.addEventListener('click', function() {
                var self = this;
                if (!self.classList.contains('is-active')) {
                    fadeOutMenu();
                }
                self.classList.toggle('is-active');
                var menu = self.nextElementSibling;
                if (menu && menu.classList.contains('js-dropdown-menu')) {
                    if (menu.style.display === 'none' || menu.style.display === '') {
                        menu.style.display = 'block';
                    } else {
                        menu.style.display = 'none';
                    }
                }
            });
        });
    
        document.addEventListener('click', function(event) {
            dropdowns.forEach(function(dropdown) {
                if (!dropdown.contains(event.target)) {
                    fadeOutMenu();
                }
            });
        });
    });
}