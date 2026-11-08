import { useParams } from "react-router-dom";

function Match() {
    const { matchId } = useParams<{matchId:string}>();

    return <h1>Battle id: {matchId} coming soon</h1>
}

export default Match;