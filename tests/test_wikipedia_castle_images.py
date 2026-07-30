from scripts.update_wikipedia_castle_images import parse_wikipedia_castle_images


def test_parse_wikipedia_castle_images_matches_gallery_to_table_row() -> None:
    """Wikipedia table rows should provide prefectures for gallery images."""
    html = """
    <div class="mw-parser-output">
      <div class="mw-heading mw-heading2"><h2>北海道</h2></div>
      <table class="wikitable">
        <tr>
          <th>No</th><th>城名</th><th>所在地</th><th>印章位置</th>
        </tr>
        <tr>
          <td>2</td>
          <td><a title="五稜郭">五稜郭</a></td>
          <td><a title="北海道">北海道</a> <a title="函館市">函館市</a></td>
          <td>箱館奉行所</td>
        </tr>
      </table>
      <ul class="gallery mw-gallery-traditional">
        <li class="gallerybox">
          <div class="thumb">
            <img
              alt="五稜郭"
              src="//upload.wikimedia.org/example/120px-goryokaku.jpg"
              srcset="//upload.wikimedia.org/example/250px-goryokaku.jpg 2x"
            />
          </div>
          <div class="gallerytext">五稜郭</div>
        </li>
      </ul>
    </div>
    """

    records = parse_wikipedia_castle_images(html)

    assert len(records) == 1
    assert records[0].name == "五稜郭"
    assert records[0].prefecture == "北海道"
    assert records[0].image_url == "https://upload.wikimedia.org/example/250px-goryokaku.jpg"


def test_parse_wikipedia_castle_images_uses_known_caption_aliases() -> None:
    """Gallery captions sometimes use short aliases instead of table names."""
    html = """
    <div class="mw-parser-output">
      <div class="mw-heading mw-heading2"><h2>東北</h2></div>
      <table class="wikitable">
        <tr>
          <th>No</th><th>城名</th><th>所在地</th><th>印章位置</th>
        </tr>
        <tr>
          <td>12</td>
          <td><a title="會津若松城">會津若松城</a></td>
          <td><a title="福島縣">福島縣</a> <a title="會津若松市">會津若松市</a></td>
          <td>天守閣</td>
        </tr>
      </table>
      <ul class="gallery mw-gallery-traditional">
        <li class="gallerybox">
          <div class="thumb">
            <img
              alt="若松城・天守"
              src="//upload.wikimedia.org/example/wakamatsu.jpg"
            />
          </div>
          <div class="gallerytext">若松城・天守</div>
        </li>
      </ul>
    </div>
    """

    records = parse_wikipedia_castle_images(html)

    assert len(records) == 1
    assert records[0].name == "會津若松城"
    assert records[0].prefecture == "福島縣"
    assert records[0].image_url == "https://upload.wikimedia.org/example/wakamatsu.jpg"
