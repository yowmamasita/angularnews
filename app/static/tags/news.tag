<news>
    <ol>
        <li each={ link in opts.links }>
            [{ link.tag }] <a href="{ link.url }" target="_blank">{ link.title }</a> (score: { link.score / 100 })
        </li>
    </ol>
</news>
